# 🔍 Supabase Schema Audit

**Chat ID:** `c72c1661-bdf4-40ad-b9a6-171761827024`
**Created At:** 1970-01-21 08:43:38
**Updated At:** 1970-01-21 08:43:46

## Chat History

### User:
# Supabase Schema Analysis Report

## Executive Summary
Overall, this is a well-structured e-commerce schema with good tracking capabilities. However, there are several critical issues and optimization opportunities identified below.

---

## 🔴 Critical Issues

### 1. **Missing Unique Constraint on `carts.user_id`**
**Problem:** Multiple carts can exist for the same user.
```sql
-- Current: No constraint
-- Expected: One cart per user

-- Fix:
CREATE UNIQUE INDEX IF NOT EXISTS carts_user_id_key ON public.carts(user_id);
```

### 2. **Conflicting RLS Policies on `anonymous_cart_items`**
**Problem:** Three overlapping policies may cause confusion:
- "Allow anonymous access to own cart items"
- "Allow service role full access"
- "Allow access to own cart items"

The third policy uses `current_setting('app.current_session_id')` which requires setting this value in your application.

**Fix:**
```sql
-- Drop redundant policies
DROP POLICY "Allow anonymous access to own cart items" ON public.anonymous_cart_items;

-- Keep only the session-based policy
CREATE POLICY "Allow access to cart items by session" 
ON public.anonymous_cart_items FOR ALL 
USING (
  cart_id IN (
    SELECT id FROM public.anonymous_carts 
    WHERE session_id = current_setting('app.current_session_id', true)::TEXT
  )
);
```

### 3. **Missing `payment_method` Column in `orders` Table**
**Problem:** Function `create_anonymous_order` references `payment_method` column that doesn't exist in the table definition.

**Fix:**
```sql
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS payment_method TEXT;
```

### 4. **Cart Items Foreign Key Mismatch**
**Problem:** `anonymous_cart_items` uses TEXT for `product_id` and `variant_id`, but `cart_items` uses UUID. This inconsistency will cause issues during cart migration.

**Fix:** Either:
- Change anonymous cart items to use UUID
- Add validation to ensure TEXT values are valid UUIDs
```sql
-- Option 1: Change to UUID
ALTER TABLE public.anonymous_cart_items 
ALTER COLUMN product_id TYPE UUID USING product_id::UUID,
ALTER COLUMN variant_id TYPE UUID USING variant_id::UUID;

-- Add foreign keys
ALTER TABLE public.anonymous_cart_items
ADD CONSTRAINT anonymous_cart_items_product_id_fkey 
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
```

---

## ⚠️ Major Issues

### 5. **Incomplete `cart_items` Unique Constraint**
**Problem:** Users can add the same product+variant multiple times.

**Fix:**
```sql
CREATE UNIQUE INDEX IF NOT EXISTS cart_items_cart_product_variant_key 
ON public.cart_items(cart_id, product_id, COALESCE(variant_id, '00000000-0000-0000-0000-000000000000'::UUID));
```

### 6. **Missing Cascade on `cart_items.variant_id`**
**Problem:** If a variant is deleted, cart items remain with orphaned variant_id.

**Fix:**
```sql
ALTER TABLE public.cart_items
ADD CONSTRAINT cart_items_variant_id_fkey 
FOREIGN KEY (variant_id) REFERENCES products(id) ON DELETE CASCADE;
-- Note: Assumes variants are in products table
```

### 7. **RLS Policy Issue on `orders`**
**Problem:** Complex UPDATE policy logic in RLS will fail. RLS policies should be simple boolean expressions.

**Current (problematic):**
```sql
CREATE POLICY "Users can update their own orders" ON public.orders 
FOR UPDATE USING (auth.uid() = user_id) 
WITH CHECK (status IS NOT DISTINCT FROM CASE WHEN ...);
```

**Fix:**
```sql
-- Drop the complex policy
DROP POLICY "Users can update their own orders" ON public.orders;

-- Create simpler policy
CREATE POLICY "Users can update their own orders" 
ON public.orders FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Handle status transitions in application code or triggers
```

### 8. **Missing Indexes for Foreign Keys**
**Problem:** Foreign key columns without indexes cause slow queries.

**Fix:**
```sql
-- Cart items
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON public.cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON public.cart_items(product_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_variant_id ON public.cart_items(variant_id) 
WHERE variant_id IS NOT NULL;

-- Order items
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON public.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_variant_id ON public.order_items(variant_id) 
WHERE variant_id IS NOT NULL;

-- Carts
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON public.carts(user_id);
```

---

## 🟡 Performance Optimization Opportunities

### 9. **Add Composite Indexes for Common Queries**
```sql
-- For cart analytics queries
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_status_created_at 
ON public.anonymous_carts(status, created_at);

-- For product searches
CREATE INDEX IF NOT EXISTS idx_products_category_in_stock 
ON public.products(category, in_stock) WHERE in_stock = true;

-- For order queries
CREATE INDEX IF NOT EXISTS idx_orders_user_status 
ON public.orders(user_id, status) WHERE user_id IS NOT NULL;

-- For experience tracking queries
CREATE INDEX IF NOT EXISTS idx_experience_tracks_session_event 
ON public.experience_tracks(session_id, event_type, created_at);
```

### 10. **Add GIN Indexes for JSONB Columns**
```sql
CREATE INDEX IF NOT EXISTS idx_products_tags_gin 
ON public.products USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_products_variants_gin 
ON public.products USING GIN(variants);

CREATE INDEX IF NOT EXISTS idx_anonymous_carts_cart_data_gin 
ON public.anonymous_carts USING GIN(cart_data);

CREATE INDEX IF NOT EXISTS idx_experience_tracks_properties_gin 
ON public.experience_tracks USING GIN(custom_properties);
```

### 11. **Optimize `update_cart_totals` Function**
**Problem:** Recalculates totals on every item change, even when unnecessary.

**Fix:**
```sql
CREATE OR REPLACE FUNCTION public.update_cart_totals(p_cart_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 🟢 Best Practice Recommendations

### 12. **Add Timestamps to All Tables**
Missing `created_at`/`updated_at` on:
- `order_items`
- `newsletter_subscriptions` (has `subscribed_at` but no `updated_at`)

```sql
ALTER TABLE public.order_items
ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
```

### 13. **Add Soft Delete Support**
Consider adding `deleted_at` columns for audit trails:
```sql
ALTER TABLE public.products
ADD COLUMN deleted_at TIMESTAMPTZ;

CREATE INDEX idx_products_deleted_at 
ON public.products(deleted_at) WHERE deleted_at IS NULL;
```

### 14. **Improve Error Handling in Functions**
Add better error messages and validation:
```sql
CREATE OR REPLACE FUNCTION public.migrate_anonymous_to_user_cart(
    p_session_id TEXT, 
    p_user_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;

    -- Rest of function...
END;
$$ LANGUAGE plpgsql;
```

### 15. **Add Check Constraints for Data Integrity**
```sql
-- Ensure positive values
ALTER TABLE public.products
ADD CONSTRAINT products_price_positive CHECK (price > 0),
ADD CONSTRAINT products_compare_at_price_positive CHECK (compare_at_price IS NULL OR compare_at_price > 0);

ALTER TABLE public.order_items
ADD CONSTRAINT order_items_price_positive CHECK (price >= 0),
ADD CONSTRAINT order_items_quantity_positive CHECK (quantity > 0);

-- Ensure rating is valid
ALTER TABLE public.products
ADD CONSTRAINT products_rating_range CHECK (rating >= 0 AND rating <= 5);
```

### 16. **Add Database-Level Validation**
```sql
-- Email validation
ALTER TABLE public.anonymous_carts
ADD CONSTRAINT anonymous_carts_email_valid 
CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE public.newsletter_subscriptions
ADD CONSTRAINT newsletter_subscriptions_email_valid 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
```

---

## 🔒 Security Considerations

### 17. **RLS Policy Gaps**
**Issue:** Some tables allow anonymous insert without proper validation.

**Recommendation:**
```sql
-- Add rate limiting considerations for anonymous operations
-- Consider adding a function to check request frequency

CREATE OR REPLACE FUNCTION check_rate_limit(p_ip_address INET)
RETURNS BOOLEAN AS $$
DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 18. **Sensitive Data in Functions**
**Issue:** `SECURITY DEFINER` functions should be reviewed carefully.

**Recommendation:**
- Review `create_anonymous_order` function
- Ensure it doesn't expose sensitive data
- Consider using `SECURITY INVOKER` where appropriate

---

## 🧹 Code Quality Issues

### 19. **Inconsistent Naming Conventions**
- Mix of snake_case and camelCase in JSONB fields
- Some functions use `p_` prefix for parameters, others don't

**Recommendation:** Standardize on snake_case throughout.

### 20. **Duplicate/Redundant Code**
Two versions of `get_cart_analytics()`:
```sql
-- One with parameters
CREATE OR REPLACE FUNCTION public.get_cart_analytics(
    p_start_date timestamp with time zone, 
    p_end_date timestamp with time zone
)

-- One without (calls the first)
CREATE OR REPLACE FUNCTION public.get_cart_analytics()
```

This is actually good practice (overloading), but should be documented.

---

## 📊 Missing Functionality

### 21. **No Inventory Management**
Consider adding:
```sql
ALTER TABLE public.products
ADD COLUMN inventory_quantity INTEGER DEFAULT 0,
ADD COLUMN inventory_policy TEXT DEFAULT 'deny' 
    CHECK (inventory_policy IN ('deny', 'continue'));

CREATE INDEX idx_products_inventory 
ON public.products(inventory_quantity) 
WHERE inventory_quantity <= 10; -- Low stock alert
```

### 22. **No Order Status History**
Track order status changes:
```sql
CREATE TABLE IF NOT EXISTS public.order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_order_status_history_order_id 
ON public.order_status_history(order_id);
```

### 23. **No Wishlist Functionality**
Common e-commerce feature:
```sql
CREATE TABLE IF NOT EXISTS public.wishlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);
```

---

## 🎯 Priority Action Items

### Immediate (Fix Now)
1. ✅ Add missing `payment_method` column to `orders`
2. ✅ Fix `cart_items` data type consistency
3. ✅ Add unique constraint on `carts.user_id`
4. ✅ Simplify complex RLS policies
5. ✅ Add missing foreign key indexes

### High Priority (This Week)
6. ✅ Add composite indexes for performance
7. ✅ Fix cart item duplicate prevention
8. ✅ Add check constraints for data validation
9. ✅ Review and fix RLS policies on `anonymous_cart_items`

### Medium Priority (This Month)
10. ✅ Add GIN indexes for JSONB columns
11. ✅ Implement soft delete
12. ✅ Add order status history
13. ✅ Add inventory management

### Low Priority (Future)
14. ✅ Add wishlist functionality
15. ✅ Implement rate limiting
16. ✅ Add comprehensive audit logging

---

## 📝 Testing Recommendations

1. **Test cart migration** from anonymous to authenticated user
2. **Test RLS policies** with different user roles
3. **Load test** cart operations with concurrent users
4. **Test trigger cascades** when deleting related records
5. **Verify** `pg_cron` jobs are scheduled correctly

---

## 🔍 Monitoring Queries

```sql
-- Check for orphaned cart items
SELECT COUNT(*) FROM public.cart_items ci
LEFT JOIN public.carts c ON ci.cart_id = c.id
WHERE c.id IS NULL;

-- Check for expired carts not marked
SELECT COUNT(*) FROM public.anonymous_carts
WHERE expires_at < NOW() AND status = 'active';

-- Check average cart abandonment time
SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/3600) as avg_hours
FROM public.anonymous_carts
WHERE status = 'abandoned';

-- Check for slow queries needing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public' AND tablename IN ('anonymous_carts', 'products', 'orders')
ORDER BY abs(correlation) ASC;
```

---

## Summary

**Total Issues Found:** 23
- 🔴 Critical: 4
- ⚠️ Major: 4
- 🟡 Performance: 3
- 🟢 Recommendations: 12

This schema is production-ready with the critical fixes applied. The performance optimizations and recommendations will improve scalability and maintainability.

#### Attached Files:
- [schema.txt](/api/v1/files/16b1dc79-6c4a-4b01-9092-a581e8103896)

### Assistant:
<details type="reasoning" done="true" duration="25" view="" last_tool_call_name="">
<summary>Thought for 25 seconds</summary>
> Let me analyze the Supabase schema provided and create a comprehensive report. I'll need to identify issues, optimizations, and recommendations.
> 
> First, let me understand the structure of the database:
> 
> 1. **Tables:**
>    - anonymous_cart_items & anonymous_carts - For guest shopping carts
>    - cart_items & carts - For authenticated user shopping carts
>    - order_items & orders - For order management
>    - products - Product catalog
>    - profiles - User profiles
>    - experience_tracks - User behavior tracking
>    - user_sessions - Session tracking
>    - user_journeys - User journey tracking
>    - performance_metrics - Performance tracking
>    - addresses - User addresses
>    - reviews - Product reviews
>    - newsletter_subscriptions - Newsletter subscriptions
> 
> 2. **Functions:**
>    - Various cart management functions
>    - Analytics functions
>    - User behavior tracking functions
>    - Data cleanup functions
> 
> 3. **Triggers:**
>    - For updating timestamps
>    - For updating cart totals
>    - For session tracking
> 
> 4. **RLS Policies:**
>    - Row Level Security policies for all tables
> 
> Now, let me identify issues and optimizations:
> 
> ### Critical Issues:
> 
> 1. **Missing Unique Constraint on `carts.user_id`**
>    - Multiple carts can exist for the same user
>    - This could lead to confusion when a user has multiple carts
> 
> 2. **Conflicting RLS Policies on `anonymous_cart_items`**
>    - Three overlapping policies that might cause confusion
>    - One policy uses `current_setting('app.current_session_id')` which requires setting this value in the application
> 
> 3. **Missing `payment_method` Column in `orders` Table**
>    - The function `create_anonymous_order` references a column that doesn't exist
> 
> 4. **Cart Items Foreign Key Mismatch**
>    - `anonymous_cart_items` uses TEXT for `product_id` and `variant_id`
>    - `cart_items` uses UUID for the same fields
>    - This inconsistency will cause issues during cart migration
> 
> ### Major Issues:
> 
> 5. **Incomplete `cart_items` Unique Constraint**
>    - Users can add the same product+variant multiple times
> 
> 6. **Missing Cascade on `cart_items.variant_id`**
>    - If a variant is deleted, cart items remain with orphaned variant_id
> 
> 7. **RLS Policy Issue on `orders`**
>    - Complex UPDATE policy logic in RLS will fail
> 
> 8. **Missing Indexes for Foreign Keys**
>    - Foreign key columns without indexes cause slow queries
> 
> ### Performance Optimization Opportunities:
> 
> 9. **Add Composite Indexes for Common Queries**
>    - For cart analytics queries
>    - For product searches
>    - For order queries
>    - For experience tracking queries
> 
> 10. **Add GIN Indexes for JSONB Columns**
>     - For products tags, variants
>     - For anonymous_carts cart_data
>     - For experience_tracks custom_properties
> 
> 11. **Optimize `update_cart_totals` Function**
>     - Recalculates totals on every item change, even when unnecessary
> 
> ### Best Practice Recommendations:
> 
> 12. **Add Timestamps to All Tables**
>     - Missing `created_at`/`updated_at` on some tables
> 
> 13. **Add Soft Delete Support**
>     - Consider adding `deleted_at` columns for audit trails
> 
> 14. **Improve Error Handling in Functions**
>     - Add better error messages and validation
> 
> 15. **Add Check Constraints for Data Integrity**
>     - Ensure positive values for prices
>     - Ensure rating is valid
> 
> 16. **Add Database-Level Validation**
>     - Email validation
> 
> ### Security Considerations:
> 
> 17. **RLS Policy Gaps**
>     - Some tables allow anonymous insert without proper validation
> 
> 18. **Sensitive Data in Functions**
>     - `SECURITY DEFINER` functions should be reviewed carefully
> 
> ### Code Quality Issues:
> 
> 19. **Inconsistent Naming Conventions**
>     - Mix of snake_case and camelCase in JSONB fields
>     - Some functions use `p_` prefix for parameters, others don't
> 
> 20. **Duplicate/Redundant Code**
>     - Two versions of `get_cart_analytics()`
> 
> ### Missing Functionality:
> 
> 21. **No Inventory Management**
>     - Consider adding inventory tracking
> 
> 22. **No Order Status History**
>     - Track order status changes
> 
> 23. **No Wishlist Functionality**
>     - Common e-commerce feature
> 
> Now I'll create a comprehensive report with these findings, including fixes and recommendations.
</details>
# Supabase Schema Analysis Report

## Executive Summary
Overall, this is a well-structured e-commerce schema with good tracking capabilities. However, there are several critical issues and optimization opportunities identified below.

---

## 🔴 Critical Issues

### 1. **Missing Unique Constraint on `carts.user_id`**
**Problem:** Multiple carts can exist for the same user.
```sql
-- Current: No constraint
-- Expected: One cart per user

-- Fix:
CREATE UNIQUE INDEX IF NOT EXISTS carts_user_id_key ON public.carts(user_id);
```

### 2. **Conflicting RLS Policies on `anonymous_cart_items`**
**Problem:** Three overlapping policies may cause confusion:
- "Allow anonymous access to own cart items"
- "Allow service role full access"
- "Allow access to own cart items"

The third policy uses `current_setting('app.current_session_id')` which requires setting this value in your application.

**Fix:**
```sql
-- Drop redundant policies
DROP POLICY "Allow anonymous access to own cart items" ON public.anonymous_cart_items;

-- Keep only the session-based policy
CREATE POLICY "Allow access to cart items by session" 
ON public.anonymous_cart_items FOR ALL 
USING (
  cart_id IN (
    SELECT id FROM public.anonymous_carts 
    WHERE session_id = current_setting('app.current_session_id', true)::TEXT
  )
);
```

### 3. **Missing `payment_method` Column in `orders` Table**
**Problem:** Function `create_anonymous_order` references `payment_method` column that doesn't exist in the table definition.

**Fix:**
```sql
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS payment_method TEXT;
```

### 4. **Cart Items Foreign Key Mismatch**
**Problem:** `anonymous_cart_items` uses TEXT for `product_id` and `variant_id`, but `cart_items` uses UUID. This inconsistency will cause issues during cart migration.

**Fix:** Either:
- Change anonymous cart items to use UUID
- Add validation to ensure TEXT values are valid UUIDs
```sql
-- Option 1: Change to UUID
ALTER TABLE public.anonymous_cart_items 
ALTER COLUMN product_id TYPE UUID USING product_id::UUID,
ALTER COLUMN variant_id TYPE UUID USING variant_id::UUID;

-- Add foreign keys
ALTER TABLE public.anonymous_cart_items
ADD CONSTRAINT anonymous_cart_items_product_id_fkey 
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
```

---

## ⚠️ Major Issues

### 5. **Incomplete `cart_items` Unique Constraint**
**Problem:** Users can add the same product+variant multiple times.

**Fix:**
```sql
CREATE UNIQUE INDEX IF NOT EXISTS cart_items_cart_product_variant_key 
ON public.cart_items(cart_id, product_id, COALESCE(variant_id, '00000000-0000-0000-0000-000000000000'::UUID));
```

### 6. **Missing Cascade on `cart_items.variant_id`**
**Problem:** If a variant is deleted, cart items remain with orphaned variant_id.

**Fix:**
```sql
ALTER TABLE public.cart_items
ADD CONSTRAINT cart_items_variant_id_fkey 
FOREIGN KEY (variant_id) REFERENCES products(id) ON DELETE CASCADE;
-- Note: Assumes variants are in products table
```

### 7. **RLS Policy Issue on `orders`**
**Problem:** Complex UPDATE policy logic in RLS will fail. RLS policies should be simple boolean expressions.

**Current (problematic):**
```sql
CREATE POLICY "Users can update their own orders" ON public.orders 
FOR UPDATE USING (auth.uid() = user_id) 
WITH CHECK (status IS NOT DISTINCT FROM CASE WHEN ...);
```

**Fix:**
```sql
-- Drop the complex policy
DROP POLICY "Users can update their own orders" ON public.orders;

-- Create simpler policy
CREATE POLICY "Users can update their own orders" 
ON public.orders FOR UPDATE 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Handle status transitions in application code or triggers
```

### 8. **Missing Indexes for Foreign Keys**
**Problem:** Foreign key columns without indexes cause slow queries.

**Fix:**
```sql
-- Cart items
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON public.cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON public.cart_items(product_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_variant_id ON public.cart_items(variant_id) 
WHERE variant_id IS NOT NULL;

-- Order items
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON public.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_variant_id ON public.order_items(variant_id) 
WHERE variant_id IS NOT NULL;

-- Carts
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON public.carts(user_id);
```

---

## 🟡 Performance Optimization Opportunities

### 9. **Add Composite Indexes for Common Queries**
```sql
-- For cart analytics queries
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_status_created_at 
ON public.anonymous_carts(status, created_at);

-- For product searches
CREATE INDEX IF NOT EXISTS idx_products_category_in_stock 
ON public.products(category, in_stock) WHERE in_stock = true;

-- For order queries
CREATE INDEX IF NOT EXISTS idx_orders_user_status 
ON public.orders(user_id, status) WHERE user_id IS NOT NULL;

-- For experience tracking queries
CREATE INDEX IF NOT EXISTS idx_experience_tracks_session_event 
ON public.experience_tracks(session_id, event_type, created_at);
```

### 10. **Add GIN Indexes for JSONB Columns**
```sql
CREATE INDEX IF NOT EXISTS idx_products_tags_gin 
ON public.products USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_products_variants_gin 
ON public.products USING GIN(variants);

CREATE INDEX IF NOT EXISTS idx_anonymous_carts_cart_data_gin 
ON public.anonymous_carts USING GIN(cart_data);

CREATE INDEX IF NOT EXISTS idx_experience_tracks_properties_gin 
ON public.experience_tracks USING GIN(custom_properties);
```

### 11. **Optimize `update_cart_totals` Function**
**Problem:** Recalculates totals on every item change, even when unnecessary.

**Fix:**
```sql
CREATE OR REPLACE FUNCTION public.update_cart_totals(p_cart_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 🟢 Best Practice Recommendations

### 12. **Add Timestamps to All Tables**
Missing `created_at`/`updated_at` on:
- `order_items`
- `newsletter_subscriptions` (has `subscribed_at` but no `updated_at`)

```sql
ALTER TABLE public.order_items
ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
```

### 13. **Add Soft Delete Support**
Consider adding `deleted_at` columns for audit trails:
```sql
ALTER TABLE public.products
ADD COLUMN deleted_at TIMESTAMPTZ;

CREATE INDEX idx_products_deleted_at 
ON public.products(deleted_at) WHERE deleted_at IS NULL;
```

### 14. **Improve Error Handling in Functions**
Add better error messages and validation:
```sql
CREATE OR REPLACE FUNCTION public.migrate_anonymous_to_user_cart(
    p_session_id TEXT, 
    p_user_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;

    -- Rest of function...
END;
$$ LANGUAGE plpgsql;
```

### 15. **Add Check Constraints for Data Integrity**
```sql
-- Ensure positive values
ALTER TABLE public.products
ADD CONSTRAINT products_price_positive CHECK (price > 0),
ADD CONSTRAINT products_compare_at_price_positive CHECK (compare_at_price IS NULL OR compare_at_price > 0);

ALTER TABLE public.order_items
ADD CONSTRAINT order_items_price_positive CHECK (price >= 0),
ADD CONSTRAINT order_items_quantity_positive CHECK (quantity > 0);

-- Ensure rating is valid
ALTER TABLE public.products
ADD CONSTRAINT products_rating_range CHECK (rating >= 0 AND rating <= 5);
```

### 16. **Add Database-Level Validation**
```sql
-- Email validation
ALTER TABLE public.anonymous_carts
ADD CONSTRAINT anonymous_carts_email_valid 
CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE public.newsletter_subscriptions
ADD CONSTRAINT newsletter_subscriptions_email_valid 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
```

---

## 🔒 Security Considerations

### 17. **RLS Policy Gaps**
**Issue:** Some tables allow anonymous insert without proper validation.

**Recommendation:**
```sql
-- Add rate limiting considerations for anonymous operations
-- Consider adding a function to check request frequency

CREATE OR REPLACE FUNCTION check_rate_limit(p_ip_address INET)
RETURNS BOOLEAN AS $$
DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 18. **Sensitive Data in Functions**
**Issue:** `SECURITY DEFINER` functions should be reviewed carefully.

**Recommendation:**
- Review `create_anonymous_order` function
- Ensure it doesn't expose sensitive data
- Consider using `SECURITY INVOKER` where appropriate

---

## 🧹 Code Quality Issues

### 19. **Inconsistent Naming Conventions**
- Mix of snake_case and camelCase in JSONB fields
- Some functions use `p_` prefix for parameters, others don't

**Recommendation:** Standardize on snake_case throughout.

### 20. **Duplicate/Redundant Code**
Two versions of `get_cart_analytics()`:
```sql
-- One with parameters
CREATE OR REPLACE FUNCTION public.get_cart_analytics(
    p_start_date timestamp with time zone, 
    p_end_date timestamp with time zone
)

-- One without (calls the first)
CREATE OR REPLACE FUNCTION public.get_cart_analytics()
```

This is actually good practice (overloading), but should be documented.

---

## 📊 Missing Functionality

### 21. **No Inventory Management**
Consider adding:
```sql
ALTER TABLE public.products
ADD COLUMN inventory_quantity INTEGER DEFAULT 0,
ADD COLUMN inventory_policy TEXT DEFAULT 'deny' 
    CHECK (inventory_policy IN ('deny', 'continue'));

CREATE INDEX idx_products_inventory 
ON public.products(inventory_quantity) 
WHERE inventory_quantity <= 10; -- Low stock alert
```

### 22. **No Order Status History**
Track order status changes:
```sql
CREATE TABLE IF NOT EXISTS public.order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_order_status_history_order_id 
ON public.order_status_history(order_id);
```

### 23. **No Wishlist Functionality**
Common e-commerce feature:
```sql
CREATE TABLE IF NOT EXISTS public.wishlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);
```

---

## 🎯 Priority Action Items

### Immediate (Fix Now)
1. ✅ Add missing `payment_method` column to `orders`
2. ✅ Fix `cart_items` data type consistency
3. ✅ Add unique constraint on `carts.user_id`
4. ✅ Simplify complex RLS policies
5. ✅ Add missing foreign key indexes

### High Priority (This Week)
6. ✅ Add composite indexes for performance
7. ✅ Fix cart item duplicate prevention
8. ✅ Add check constraints for data validation
9. ✅ Review and fix RLS policies on `anonymous_cart_items`

### Medium Priority (This Month)
10. ✅ Add GIN indexes for JSONB columns
11. ✅ Implement soft delete
12. ✅ Add order status history
13. ✅ Add inventory management

### Low Priority (Future)
14. ✅ Add wishlist functionality
15. ✅ Implement rate limiting
16. ✅ Add comprehensive audit logging

---

## 📝 Testing Recommendations

1. **Test cart migration** from anonymous to authenticated user
2. **Test RLS policies** with different user roles
3. **Load test** cart operations with concurrent users
4. **Test trigger cascades** when deleting related records
5. **Verify** `pg_cron` jobs are scheduled correctly

---

## 🔍 Monitoring Queries

```sql
-- Check for orphaned cart items
SELECT COUNT(*) FROM public.cart_items ci
LEFT JOIN public.carts c ON ci.cart_id = c.id
WHERE c.id IS NULL;

-- Check for expired carts not marked
SELECT COUNT(*) FROM public.anonymous_carts
WHERE expires_at < NOW() AND status = 'active';

-- Check average cart abandonment time
SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/3600) as avg_hours
FROM public.anonymous_carts
WHERE status = 'abandoned';

-- Check for slow queries needing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public' AND tablename IN ('anonymous_carts', 'products', 'orders')
ORDER BY abs(correlation) ASC;
```

---

## Summary

**Total Issues Found:** 23
- 🔴 Critical: 4
- ⚠️ Major: 4
- 🟡 Performance: 3
- 🟢 Recommendations: 12

This schema is production-ready with the critical fixes applied. The performance optimizations and recommendations will improve scalability and maintainability.

### User:
output full schema.sql with fixes

### Assistant:
<details type="reasoning" done="true" duration="3" view="" last_tool_call_name="">
<summary>Thought for 3 seconds</summary>
> The user wants me to generate a complete schema.sql file with all the fixes I identified in my analysis. I need to:
> 
> 1. Start with the original schema
> 2. Apply all the critical fixes first
> 3. Apply major issues fixes
> 4. Apply performance optimizations
> 5. Apply best practice recommendations
> 6. Maintain the original structure and organization
> 
> Let me go through each fix systematically:
> 
> Critical Fixes:
> 1. Add unique constraint on carts.user_id
> 2. Fix conflicting RLS policies on anonymous_cart_items
> 3. Add missing payment_method column to orders
> 4. Fix cart items foreign key mismatch (change TEXT to UUID)
> 
> Major Issues:
> 5. Add unique constraint on cart_items (cart_id, product_id, variant_id)
> 6. Add missing cascade on cart_items.variant_id
> 7. Fix RLS policy issue on orders
> 8. Add missing indexes for foreign keys
> 
> Performance Optimizations:
> 9. Add composite indexes
> 10. Add GIN indexes for JSONB columns
> 11. Optimize update_cart_totals function
> 
> Best Practices:
> 12. Add timestamps to order_items
> 13. Add soft delete support (optional, I'll include but commented)
> 14. Improve error handling in functions
> 15. Add check constraints
> 16. Add database-level validation
> 
> I'll maintain the original structure with sections for Extensions, Tables, Indexes, Constraints, Functions, Triggers, RLS Policies, and Comments.
</details>
```sql
-- Combined Schema for Supabase Project: originz
-- Generated from migration files
-- Updated with critical fixes and optimizations

-- =================================================================
-- Extensions
-- =================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- =================================================================
-- Tables
-- =================================================================

-- anon cart items
CREATE TABLE IF NOT EXISTS "public"."anonymous_cart_items" (
    "id" uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    "cart_id" uuid,
    "product_id" uuid NOT NULL, -- Changed from TEXT to UUID
    "variant_id" uuid, -- Changed from TEXT to UUID
    "product_title" text,
    "product_image" text,
    "price" numeric(10, 2) NOT NULL,
    "quantity" integer NOT NULL,
    "added_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now()
);
ALTER TABLE "public"."anonymous_cart_items" ENABLE ROW LEVEL SECURITY;

-- anon carts
CREATE TABLE IF NOT EXISTS "public"."anonymous_carts" (
    "id" uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    "session_id" text NOT NULL,
    "expires_at" timestamp with time zone NOT NULL DEFAULT (now() + '7 days'::interval),
    "email" text,
    "phone" text,
    "cart_data" jsonb DEFAULT '{}'::jsonb,
    "total_value" numeric(10, 2) DEFAULT 0,
    "item_count" integer DEFAULT 0,
    "utm_source" text,
    "utm_medium" text,
    "utm_campaign" text,
    "referrer" text,
    "user_agent" text,
    "ip_address" text,
    "status" text DEFAULT 'active'::text,
    "created_at" timestamp with time zone DEFAULT now(),
    "updated_at" timestamp with time zone DEFAULT now()
);
ALTER TABLE "public"."anonymous_carts" ENABLE ROW LEVEL SECURITY;

-- cart items
CREATE TABLE IF NOT EXISTS "public"."cart_items" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "cart_id" uuid,
    "product_id" uuid,
    "variant_id" uuid,
    "quantity" integer NOT NULL,
    "created_at" timestamp with time zone NOT NULL DEFAULT now(),
    "updated_at" timestamp with time zone NOT NULL DEFAULT now()
);
ALTER TABLE "public"."cart_items" ENABLE ROW LEVEL SECURITY;

-- carts
CREATE TABLE IF NOT EXISTS "public"."carts" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid,
    "created_at" timestamp with time zone NOT NULL DEFAULT now(),
    "updated_at" timestamp with time zone NOT NULL DEFAULT now()
);
ALTER TABLE "public"."carts" ENABLE ROW LEVEL SECURITY;

-- order items
CREATE TABLE IF NOT EXISTS "public"."order_items" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "order_id" uuid,
    "product_id" uuid,
    "variant_id" uuid,
    "quantity" integer NOT NULL,
    "price" numeric(10, 2) NOT NULL,
    "created_at" timestamp with time zone NOT NULL DEFAULT now(),
    "updated_at" timestamp with time zone NOT NULL DEFAULT now() -- Added missing timestamp
);
ALTER TABLE "public"."order_items" ENABLE ROW LEVEL SECURITY;

-- orders
CREATE TABLE IF NOT EXISTS "public"."orders" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid,
    "created_at" timestamp with time zone NOT NULL DEFAULT now(),
    "status" text NOT NULL DEFAULT 'Pending'::text,
    "total" numeric(10, 2) NOT NULL,
    "shipping_address" jsonb,
    "billing_address" jsonb,
    "anonymous_cart_id" UUID,
    "payment_method" TEXT -- Added missing column
);
ALTER TABLE "public"."orders" ENABLE ROW LEVEL SECURITY;

-- products
CREATE TABLE IF NOT EXISTS "public"."products" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "title" text NOT NULL,
    "handle" text NOT NULL,
    "description" text,
    "price" numeric(10, 2) NOT NULL,
    "compare_at_price" numeric(10, 2),
    "images" jsonb NOT NULL DEFAULT '[]'::jsonb,
    "category" text,
    "in_stock" boolean NOT NULL DEFAULT true,
    "rating" numeric(2, 1) NOT NULL DEFAULT 0.0,
    "review_count" integer NOT NULL DEFAULT 0,
    "tags" text [] NOT NULL DEFAULT '{}'::text [],
    "vendor" text,
    "variants" jsonb NOT NULL DEFAULT '[]'::jsonb,
    "options" jsonb NOT NULL DEFAULT '[]'::jsonb,
    "created_at" timestamp with time zone NOT NULL DEFAULT now(),
    "updated_at" timestamp with time zone NOT NULL DEFAULT now()
    -- "deleted_at" timestamp with time zone -- Uncomment for soft delete support
);
ALTER TABLE "public"."products" ENABLE ROW LEVEL SECURITY;

-- profiles
CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "id" uuid NOT NULL,
    "full_name" text,
    "avatar_url" text,
    "billing_address" jsonb,
    "shipping_address" jsonb,
    "updated_at" timestamp with time zone DEFAULT now()
);
ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;

-- experience_tracks
CREATE TABLE IF NOT EXISTS public.experience_tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    user_id UUID,
    anonymous_id TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('page_view', 'click', 'scroll', 'form_interaction', 'product_view', 'add_to_cart', 'search', 'filter', 'sort', 'hover', 'video_interaction', 'image_interaction', 'checkout_step', 'error', 'performance')),
    event_name TEXT NOT NULL,
    page_url TEXT NOT NULL,
    page_title TEXT,
    element_selector TEXT,
    element_text TEXT,
    element_position JSONB,
    interaction_data JSONB DEFAULT '{}',
    custom_properties JSONB DEFAULT '{}',
    user_agent TEXT,
    viewport_width INTEGER,
    viewport_height INTEGER,
    screen_width INTEGER,
    screen_height INTEGER,
    device_type TEXT,
    browser_name TEXT,
    browser_version TEXT,
    os_name TEXT,
    os_version TEXT,
    page_load_time INTEGER,
    time_on_page INTEGER,
    scroll_depth INTEGER,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_term TEXT,
    utm_content TEXT,
    referrer_url TEXT,
    ip_address INET,
    country_code TEXT,
    city TEXT,
    timezone TEXT,
    client_timestamp TIMESTAMPTZ,
    server_timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.experience_tracks ENABLE ROW LEVEL SECURITY;

-- user_sessions
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID,
    anonymous_id TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration INTEGER,
    page_views INTEGER DEFAULT 0,
    interactions INTEGER DEFAULT 0,
    entry_url TEXT,
    entry_page_title TEXT,
    exit_url TEXT,
    exit_page_title TEXT,
    user_agent TEXT,
    device_type TEXT,
    browser_name TEXT,
    os_name TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    referrer_url TEXT,
    ip_address INET,
    country_code TEXT,
    city TEXT,
    bounce BOOLEAN DEFAULT FALSE,
    converted BOOLEAN DEFAULT FALSE,
    conversion_value DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- user_journeys
CREATE TABLE IF NOT EXISTS public.user_journeys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    anonymous_id TEXT,
    session_id TEXT,
    journey_type TEXT NOT NULL CHECK (journey_type IN ('product_discovery', 'purchase_funnel', 'onboarding', 'support', 'content_engagement')),
    journey_step TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    page_url TEXT,
    action_taken TEXT,
    time_spent INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    dropped_off BOOLEAN DEFAULT FALSE,
    conversion_value DECIMAL(10,2),
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.user_journeys ENABLE ROW LEVEL SECURITY;

-- performance_metrics
CREATE TABLE IF NOT EXISTS public.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    page_url TEXT NOT NULL,
    lcp DECIMAL(8,2),
    fid DECIMAL(8,2),
    cls DECIMAL(6,4),
    fcp DECIMAL(8,2),
    ttfb DECIMAL(8,2),
    dns_lookup_time INTEGER,
    tcp_connect_time INTEGER,
    tls_setup_time INTEGER,
    request_time INTEGER,
    response_time INTEGER,
    dom_processing_time INTEGER,
    load_event_time INTEGER,
    custom_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;

-- addresses
CREATE TABLE IF NOT EXISTS public.addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('shipping', 'billing')),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE public.addresses ENABLE ROW LEVEL SECURITY;

-- reviews
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (product_id, user_id)
);
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

-- newsletter_subscriptions
CREATE TABLE IF NOT EXISTS public.newsletter_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW() -- Added missing timestamp
);
ALTER TABLE public.newsletter_subscriptions ENABLE ROW LEVEL SECURITY;

-- order_status_history (NEW TABLE)
CREATE TABLE IF NOT EXISTS public.order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =================================================================
-- Indexes
-- =================================================================
CREATE UNIQUE INDEX IF NOT EXISTS anonymous_cart_items_pkey ON public.anonymous_cart_items USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS anonymous_carts_pkey ON public.anonymous_carts USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS anonymous_carts_session_id_key ON public.anonymous_carts USING btree (session_id);
CREATE UNIQUE INDEX IF NOT EXISTS cart_items_pkey ON public.cart_items USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS carts_pkey ON public.carts USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS carts_user_id_key ON public.carts(user_id); -- Added unique constraint
CREATE INDEX IF NOT EXISTS idx_anonymous_cart_items_cart_id ON public.anonymous_cart_items USING btree (cart_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_cart_items_product_id ON public.anonymous_cart_items USING btree (product_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_cart_items_variant_id ON public.anonymous_cart_items USING btree (variant_id) WHERE (variant_id IS NOT NULL);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_email ON public.anonymous_carts USING btree (email) WHERE (email IS NOT NULL);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_expires_at ON public.anonymous_carts USING btree (expires_at);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_session_id ON public.anonymous_carts USING btree (session_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_status ON public.anonymous_carts USING btree (status);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_utm_source ON public.anonymous_carts USING btree (utm_source) WHERE (utm_source IS NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS order_items_pkey ON public.order_items USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS orders_pkey ON public.orders USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS products_handle_key ON public.products USING btree (handle);
CREATE UNIQUE INDEX IF NOT EXISTS products_pkey ON public.products USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS profiles_pkey ON public.profiles USING btree (id);

-- Composite indexes for performance
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_status_created_at ON public.anonymous_carts(status, created_at);
CREATE INDEX IF NOT EXISTS idx_products_category_in_stock ON public.products(category, in_stock) WHERE in_stock = true;
CREATE INDEX IF NOT EXISTS idx_orders_user_status ON public.orders(user_id, status) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_experience_tracks_session_event ON public.experience_tracks(session_id, event_type, created_at);

-- GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_products_tags_gin ON public.products USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_products_variants_gin ON public.products USING GIN(variants);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_cart_data_gin ON public.anonymous_carts USING GIN(cart_data);
CREATE INDEX IF NOT EXISTS idx_experience_tracks_properties_gin ON public.experience_tracks USING GIN(custom_properties);

-- Missing foreign key indexes
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON public.cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON public.cart_items(product_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_variant_id ON public.cart_items(variant_id) WHERE variant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON public.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_variant_id ON public.order_items(variant_id) WHERE variant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON public.carts(user_id);

-- Unique constraint for cart items
CREATE UNIQUE INDEX IF NOT EXISTS cart_items_cart_product_variant_key 
ON public.cart_items(cart_id, product_id, COALESCE(variant_id, '00000000-0000-0000-0000-000000000000'::UUID));

-- Additional indexes from original
CREATE INDEX IF NOT EXISTS idx_experience_tracks_session_id ON public.experience_tracks(session_id);
CREATE INDEX IF NOT EXISTS idx_experience_tracks_user_id ON public.experience_tracks(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_experience_tracks_anonymous_id ON public.experience_tracks(anonymous_id) WHERE anonymous_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_experience_tracks_event_type ON public.experience_tracks(event_type);
CREATE INDEX IF NOT EXISTS idx_experience_tracks_page_url ON public.experience_tracks(page_url);
CREATE INDEX IF NOT EXISTS idx_experience_tracks_created_at ON public.experience_tracks(created_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON public.user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_sessions_started_at ON public.user_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_user_journeys_user_id ON public.user_journeys(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_journeys_anonymous_id ON public.user_journeys(anonymous_id) WHERE anonymous_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_journeys_journey_type ON public.user_journeys(journey_type);
CREATE INDEX IF NOT EXISTS idx_user_journeys_session_id ON public.user_journeys(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_session_id ON public.performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_page_url ON public.performance_metrics(page_url);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_created_at ON public.performance_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_anonymous_carts_updated_at ON public.anonymous_carts(updated_at);
CREATE INDEX IF NOT EXISTS idx_orders_anonymous_cart_id ON public.orders(anonymous_cart_id) WHERE anonymous_cart_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON public.orders(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON public.addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON public.reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON public.reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_order_id ON public.order_status_history(order_id);

-- Soft delete index (uncomment if using soft delete)
-- CREATE INDEX IF NOT EXISTS idx_products_deleted_at ON public.products(deleted_at) WHERE deleted_at IS NULL;

-- =================================================================
-- Primary Keys & Foreign Keys & Constraints
-- =================================================================

-- Primary Keys
ALTER TABLE "public"."anonymous_cart_items" ADD CONSTRAINT "anonymous_cart_items_pkey" PRIMARY KEY USING INDEX "anonymous_cart_items_pkey";
ALTER TABLE "public"."anonymous_carts" ADD CONSTRAINT "anonymous_carts_pkey" PRIMARY KEY USING INDEX "anonymous_carts_pkey";
ALTER TABLE "public"."cart_items" ADD CONSTRAINT "cart_items_pkey" PRIMARY KEY USING INDEX "cart_items_pkey";
ALTER TABLE "public"."carts" ADD CONSTRAINT "carts_pkey" PRIMARY KEY USING INDEX "carts_pkey";
ALTER TABLE "public"."order_items" ADD CONSTRAINT "order_items_pkey" PRIMARY KEY USING INDEX "order_items_pkey";
ALTER TABLE "public"."orders" ADD CONSTRAINT "orders_pkey" PRIMARY KEY USING INDEX "orders_pkey";
ALTER TABLE "public"."products" ADD CONSTRAINT "products_pkey" PRIMARY KEY USING INDEX "products_pkey";
ALTER TABLE "public"."profiles" ADD CONSTRAINT "profiles_pkey" PRIMARY KEY USING INDEX "profiles_pkey";

-- Foreign Keys & Constraints
ALTER TABLE "public"."anonymous_cart_items" ADD CONSTRAINT "anonymous_cart_items_cart_id_fkey" FOREIGN KEY (cart_id) REFERENCES anonymous_carts(id) ON DELETE CASCADE;
ALTER TABLE "public"."anonymous_cart_items" ADD CONSTRAINT "anonymous_cart_items_quantity_check" CHECK ((quantity > 0));
ALTER TABLE "public"."anonymous_carts" ADD CONSTRAINT "anonymous_carts_session_id_key" UNIQUE USING INDEX "anonymous_carts_session_id_key";
ALTER TABLE "public"."anonymous_carts" ADD CONSTRAINT "anonymous_carts_status_check" CHECK (((status = ANY (ARRAY['active'::text, 'abandoned'::text, 'converted'::text, 'expired'::text]))));
ALTER TABLE "public"."cart_items" ADD CONSTRAINT "cart_items_cart_id_fkey" FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE;
ALTER TABLE "public"."cart_items" ADD CONSTRAINT "cart_items_product_id_fkey" FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
ALTER TABLE "public"."cart_items" ADD CONSTRAINT "cart_items_variant_id_fkey" FOREIGN KEY (variant_id) REFERENCES products(id) ON DELETE CASCADE; -- Added missing constraint
ALTER TABLE "public"."carts" ADD CONSTRAINT "carts_user_id_fkey" FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
ALTER TABLE "public"."order_items" ADD CONSTRAINT "order_items_order_id_fkey" FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;
ALTER TABLE "public"."order_items" ADD CONSTRAINT "order_items_product_id_fkey" FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL;
ALTER TABLE "public"."orders" ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE "public"."orders" ADD CONSTRAINT "orders_anonymous_cart_id_fkey" FOREIGN KEY (anonymous_cart_id) REFERENCES public.anonymous_carts(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."orders" ADD CONSTRAINT "orders_user_id_fkey" FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
ALTER TABLE "public"."orders" ADD CONSTRAINT orders_user_or_anonymous_check CHECK (((user_id IS NOT NULL) OR (anonymous_cart_id IS NOT NULL)));
ALTER TABLE "public"."products" ADD CONSTRAINT "products_handle_key" UNIQUE USING INDEX "products_handle_key";
ALTER TABLE "public"."profiles" ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Added foreign key for anonymous_cart_items
ALTER TABLE "public"."anonymous_cart_items" ADD CONSTRAINT "anonymous_cart_items_product_id_fkey" FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;

-- Check constraints for data integrity
ALTER TABLE public.products
ADD CONSTRAINT products_price_positive CHECK (price > 0),
ADD CONSTRAINT products_compare_at_price_positive CHECK (compare_at_price IS NULL OR compare_at_price > 0),
ADD CONSTRAINT products_rating_range CHECK (rating >= 0 AND rating <= 5);

ALTER TABLE public.order_items
ADD CONSTRAINT order_items_price_positive CHECK (price >= 0),
ADD CONSTRAINT order_items_quantity_positive CHECK (quantity > 0);

-- Email validation constraints
ALTER TABLE public.anonymous_carts
ADD CONSTRAINT anonymous_carts_email_valid 
CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE public.newsletter_subscriptions
ADD CONSTRAINT newsletter_subscriptions_email_valid 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- =================================================================
-- Functions
-- =================================================================

CREATE OR REPLACE FUNCTION public.update_updated_at_column() RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$;

CREATE OR REPLACE FUNCTION public.get_cart_analytics(p_start_date timestamp with time zone, p_end_date timestamp with time zone)
RETURNS TABLE(date DATE, active_carts INTEGER, abandoned_carts INTEGER, converted_carts INTEGER, avg_cart_value NUMERIC(10,2), avg_items_per_cart NUMERIC(10,2))
LANGUAGE plpgsql AS $function$
BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            DATE(created_at) AS date,
            COUNT(*) FILTER (WHERE status = 'active') AS active_carts,
            COUNT(*) FILTER (WHERE status = 'abandoned') AS abandoned_carts,
            COUNT(*) FILTER (WHERE status = 'converted') AS converted_carts,
            AVG(total_value) FILTER (WHERE status = 'converted') AS avg_cart_value,
            AVG(item_count) FILTER (WHERE status = 'converted') AS avg_items_per_cart
        FROM public.anonymous_carts
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(created_at)
    )
    SELECT 
        ds.date,
        COALESCE(ds.active_carts, 0)::INTEGER,
        COALESCE(ds.abandoned_carts, 0)::INTEGER,
        COALESCE(ds.converted_carts, 0)::INTEGER,
        COALESCE(ds.avg_cart_value, 0)::NUMERIC(10,2),
        COALESCE(ds.avg_items_per_cart, 0)::NUMERIC(10,2)
    FROM daily_stats ds
    ORDER BY ds.date;
END;
$function$;

CREATE OR REPLACE FUNCTION public.get_cart_analytics()
RETURNS TABLE(date DATE, active_carts INTEGER, abandoned_carts INTEGER, converted_carts INTEGER, avg_cart_value NUMERIC(10,2), avg_items_per_cart NUMERIC(10,2))
LANGUAGE plpgsql AS $function$
BEGIN
    RETURN QUERY SELECT * FROM public.get_cart_analytics(
        (NOW() - INTERVAL '30 days'),
        NOW()
    );
END;
$function$;

CREATE OR REPLACE FUNCTION public.mark_abandoned_carts(abandonment_minutes INTEGER DEFAULT 30)
RETURNS INTEGER LANGUAGE plpgsql AS $function$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH abandoned_carts AS (
        UPDATE public.anonymous_carts
        SET status = 'abandoned',
            updated_at = NOW()
        WHERE status = 'active'
        AND updated_at < (NOW() - (abandonment_minutes * INTERVAL '1 minute'))
        RETURNING 1
    )
    SELECT COUNT(*) INTO updated_count FROM abandoned_carts;
    
    RETURN updated_count;
END;
$function$;

CREATE OR REPLACE FUNCTION public.update_cart_totals(p_cart_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.trigger_update_cart_totals()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM public.update_cart_totals(OLD.cart_id);
        RETURN OLD;
    ELSE
        PERFORM public.update_cart_totals(NEW.cart_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_sessions (
        session_id, user_id, anonymous_id, started_at, entry_url, entry_page_title,
        user_agent, device_type, browser_name, os_name,
        utm_source, utm_medium, utm_campaign, referrer_url,
        ip_address, country_code, city, page_views, interactions
    )
    VALUES (
        NEW.session_id, NEW.user_id, NEW.anonymous_id, NEW.created_at, NEW.page_url, NEW.page_title,
        NEW.user_agent, NEW.device_type, NEW.browser_name, NEW.os_name,
        NEW.utm_source, NEW.utm_medium, NEW.utm_campaign, NEW.referrer_url,
        NEW.ip_address, NEW.country_code, NEW.city, 
        CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END
    )
    ON CONFLICT (session_id) DO UPDATE SET
        user_id = COALESCE(NEW.user_id, user_sessions.user_id),
        ended_at = NEW.created_at,
        exit_url = NEW.page_url,
        exit_page_title = NEW.page_title,
        page_views = user_sessions.page_views + CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        interactions = user_sessions.interactions + CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END,
        duration = EXTRACT(EPOCH FROM (NEW.created_at - user_sessions.started_at))::INTEGER,
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION mark_bounce_sessions()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.user_sessions 
    SET bounce = TRUE, updated_at = NOW()
    WHERE page_views <= 1 
      AND duration < 30 
      AND bounce = FALSE
      AND ended_at < (NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_funnel_conversion(p_journey_type TEXT, p_start_date TIMESTAMPTZ DEFAULT (NOW() - INTERVAL '30 days'), p_end_date TIMESTAMPTZ DEFAULT NOW())
RETURNS TABLE (step TEXT, step_order INTEGER, users BIGINT, conversion_rate DECIMAL) AS $$
BEGIN
    RETURN QUERY
    WITH funnel_steps AS (
        SELECT 
            journey_step,
            step_order,
            COUNT(DISTINCT COALESCE(user_id::TEXT, anonymous_id)) as step_users
        FROM public.user_journeys
        WHERE journey_type = p_journey_type
          AND created_at BETWEEN p_start_date AND p_end_date
        GROUP BY journey_step, step_order
        ORDER BY step_order
    ),
    first_step AS (
        SELECT step_users as first_step_users
        FROM funnel_steps
        ORDER BY step_order
        LIMIT 1
    )
    SELECT 
        fs.journey_step,
        fs.step_order,
        fs.step_users,
        CASE 
            WHEN fst.first_step_users > 0 THEN 
                ROUND((fs.step_users::DECIMAL / fst.first_step_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    CROSS JOIN first_step fst
    ORDER BY fs.step_order;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user_behavior_insights(p_start_date TIMESTAMPTZ DEFAULT (NOW() - INTERVAL '7 days'), p_end_date TIMESTAMPTZ DEFAULT NOW())
RETURNS TABLE (metric_name TEXT, metric_value DECIMAL, metric_unit TEXT, comparison_period_value DECIMAL, change_percentage DECIMAL) AS $$
BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN 
            p_start_date - (p_end_date - p_start_date) AND 
            p_start_date
    )
    SELECT 
        'Total Sessions'::TEXT,
        cp.total_sessions::DECIMAL,
        'count'::TEXT,
        pp.total_sessions::DECIMAL,
        CASE WHEN pp.total_sessions > 0 THEN ROUND(((cp.total_sessions - pp.total_sessions)::DECIMAL / pp.total_sessions) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Time on Page'::TEXT,
        ROUND(cp.avg_time_on_page, 2),
        'seconds'::TEXT,
        ROUND(pp.avg_time_on_page, 2),
        CASE WHEN pp.avg_time_on_page > 0 THEN ROUND(((cp.avg_time_on_page - pp.avg_time_on_page) / pp.avg_time_on_page) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Scroll Depth'::TEXT,
        ROUND(cp.avg_scroll_depth, 2),
        'percentage'::TEXT,
        ROUND(pp.avg_scroll_depth, 2),
        CASE WHEN pp.avg_scroll_depth > 0 THEN ROUND(((cp.avg_scroll_depth - pp.avg_scroll_depth) / pp.avg_scroll_depth) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_experience_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.experience_tracks WHERE created_at < (NOW() - INTERVAL '90 days');
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM public.user_sessions WHERE created_at < (NOW() - INTERVAL '90 days');
    DELETE FROM public.performance_metrics WHERE created_at < (NOW() - INTERVAL '30 days');
    DELETE FROM public.user_journeys WHERE created_at < (NOW() - INTERVAL '90 days');
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.cleanup_expired_carts()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.anonymous_carts
        WHERE expires_at < NOW()
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.migrate_anonymous_to_user_cart(p_session_id TEXT, p_user_id UUID)
RETURNS UUID AS $$
DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;
    
    SELECT id INTO v_anonymous_cart_id
    FROM public.anonymous_carts
    WHERE session_id = p_session_id
    AND status = 'active';
    
    IF v_anonymous_cart_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    INSERT INTO public.carts (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id)
    DO UPDATE SET updated_at = NOW()
    RETURNING id INTO v_cart_id;
    
    INSERT INTO public.cart_items (cart_id, product_id, variant_id, quantity)
    SELECT v_cart_id, product_id, variant_id, quantity
    FROM public.anonymous_cart_items
    WHERE cart_id = v_anonymous_cart_id
    ON CONFLICT (cart_id, product_id, variant_id) 
    DO UPDATE SET 
        quantity = cart_items.quantity + EXCLUDED.quantity,
        updated_at = NOW();
    
    UPDATE public.anonymous_carts
    SET status = 'converted',
        updated_at = NOW()
    WHERE id = v_anonymous_cart_id;
    
    RETURN v_cart_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.get_cart_by_session(p_session_id TEXT)
RETURNS TABLE(cart_id UUID, session_id TEXT, status TEXT, item_count INTEGER, total_value DECIMAL(10,2), created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ac.id AS cart_id,
        ac.session_id,
        ac.status,
        COALESCE(SUM(aci.quantity), 0)::INTEGER AS item_count,
        COALESCE(SUM(aci.price * aci.quantity), 0)::DECIMAL(10,2) AS total_value,
        ac.created_at,
        ac.updated_at
    FROM public.anonymous_carts ac
    LEFT JOIN public.anonymous_cart_items aci ON ac.id = aci.cart_id
    WHERE ac.session_id = p_session_id
    GROUP BY ac.id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.schedule_cart_cleanup_jobs()
RETURNS VOID AS $$
BEGIN
    PERFORM cron.schedule('mark-abandoned-carts', '0 * * * *', $$SELECT public.mark_abandoned_carts(30)$$);
    PERFORM cron.schedule('cleanup-expired-carts', '0 3 * * *', $$SELECT public.cleanup_expired_carts()$$);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.unschedule_cart_cleanup_jobs()
RETURNS VOID AS $$
BEGIN
    PERFORM cron.unschedule('mark-abandoned-carts');
    PERFORM cron.unschedule('cleanup-expired-carts');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.recover_abandoned_cart(p_session_id TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_updated_rows INTEGER;
BEGIN
    UPDATE public.anonymous_carts
    SET status = 'active',
        updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'abandoned';
    
    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
    RETURN v_updated_rows > 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.create_anonymous_order(p_anonymous_cart_id UUID, p_shipping_address JSONB, p_billing_address JSONB, p_payment_method TEXT, p_status TEXT DEFAULT 'pending')
RETURNS UUID AS $$
DECLARE
    v_order_id UUID;
    v_cart_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_anonymous_cart_id IS NULL OR p_shipping_address IS NULL OR p_payment_method IS NULL THEN
        RAISE EXCEPTION 'Cart ID, shipping address, and payment method are required';
    END IF;
    
    SELECT EXISTS (
        SELECT 1
        FROM public.anonymous_carts
        WHERE id = p_anonymous_cart_id AND status = 'active'
    ) INTO v_cart_exists;

    IF NOT v_cart_exists THEN
        RAISE EXCEPTION 'Invalid or inactive anonymous cart';
    END IF;

    INSERT INTO public.orders (anonymous_cart_id, status, shipping_address, billing_address, payment_method, created_at, updated_at, total)
    VALUES (p_anonymous_cart_id, p_status, p_shipping_address, p_billing_address, p_payment_method, NOW(), NOW(), (SELECT total_value FROM public.anonymous_carts WHERE id = p_anonymous_cart_id))
    RETURNING id INTO v_order_id;

    UPDATE public.anonymous_carts
    SET status = 'converted', updated_at = NOW()
    WHERE id = p_anonymous_cart_id;

    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_order_with_cart(p_order_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'order_id', o.id,
        'status', o.status,
        'created_at', o.created_at,
        'updated_at', o.updated_at,
        'shipping_address', o.shipping_address,
        'billing_address', o.billing_address,
        'payment_method', o.payment_method,
        'is_guest_order', o.user_id IS NULL,
        'cart', CASE
            WHEN o.anonymous_cart_id IS NOT NULL THEN (
                SELECT jsonb_build_object(
                    'cart_id', ac.id,
                    'session_id', ac.session_id,
                    'created_at', ac.created_at,
                    'items', COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'product_id', aci.product_id,
                            'variant_id', aci.variant_id,
                            'product_title', aci.product_title,
                            'product_image', aci.product_image,
                            'price', aci.price,
                            'quantity', aci.quantity
                        ))
                        FROM public.anonymous_cart_items aci
                        WHERE aci.cart_id = ac.id
                    ), '[]'::jsonb)
                )
                FROM public.anonymous_carts ac
                WHERE ac.id = o.anonymous_cart_id
            )
            ELSE NULL
        END,
        'user', CASE
            WHEN o.user_id IS NOT NULL THEN (
                SELECT jsonb_build_object('id', u.id, 'email', u.email)
                FROM auth.users u
                WHERE u.id = o.user_id
            )
            ELSE NULL
        END
    ) INTO v_result
    FROM public.orders o
    WHERE o.id = p_order_id;
    RETURN v_result;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION public.sync_order_cart_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'converted' AND OLD.status != 'converted' THEN
        UPDATE public.orders
        SET status = 'processing', updated_at = NOW()
        WHERE anonymous_cart_id = NEW.id AND status = 'pending';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Rate limiting function
CREATE OR REPLACE FUNCTION check_rate_limit(p_ip_address INET)
RETURNS BOOLEAN AS $$
DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =================================================================
-- Triggers
-- =================================================================
DROP TRIGGER IF EXISTS trigger_update_anonymous_cart_items_updated_at ON public.anonymous_cart_items;
CREATE TRIGGER trigger_update_anonymous_cart_items_updated_at BEFORE UPDATE ON public.anonymous_cart_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_update_cart_totals_on_delete ON public.anonymous_cart_items;
CREATE TRIGGER trigger_update_cart_totals_on_delete AFTER DELETE ON public.anonymous_cart_items FOR EACH ROW EXECUTE FUNCTION public.trigger_update_cart_totals();

DROP TRIGGER IF EXISTS trigger_update_cart_totals_on_insert ON public.anonymous_cart_items;
CREATE TRIGGER trigger_update_cart_totals_on_insert AFTER INSERT ON public.anonymous_cart_items FOR EACH ROW EXECUTE FUNCTION public.trigger_update_cart_totals();

DROP TRIGGER IF EXISTS trigger_update_cart_totals_on_update ON public.anonymous_cart_items;
CREATE TRIGGER trigger_update_cart_totals_on_update AFTER UPDATE ON public.anonymous_cart_items FOR EACH ROW WHEN (OLD.quantity IS DISTINCT FROM NEW.quantity OR OLD.price IS DISTINCT FROM NEW.price) EXECUTE FUNCTION public.trigger_update_cart_totals();

DROP TRIGGER IF EXISTS trigger_update_anonymous_carts_updated_at ON public.anonymous_carts;
CREATE TRIGGER trigger_update_anonymous_carts_updated_at BEFORE UPDATE ON public.anonymous_carts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_update_session_stats ON public.experience_tracks;
CREATE TRIGGER trigger_update_session_stats AFTER INSERT ON public.experience_tracks FOR EACH ROW EXECUTE FUNCTION update_session_stats();

DROP TRIGGER IF EXISTS trg_sync_order_cart_status ON public.anonymous_carts;
CREATE TRIGGER trg_sync_order_cart_status AFTER UPDATE OF status ON public.anonymous_carts FOR EACH ROW WHEN (OLD.status IS DISTINCT FROM NEW.status) EXECUTE FUNCTION public.sync_order_cart_status();

-- Trigger for order_items updated_at
DROP TRIGGER IF EXISTS trigger_update_order_items_updated_at ON public.order_items;
CREATE TRIGGER trigger_update_order_items_updated_at BEFORE UPDATE ON public.order_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for newsletter_subscriptions updated_at
DROP TRIGGER IF EXISTS trigger_update_newsletter_subscriptions_updated_at ON public.newsletter_subscriptions;
CREATE TRIGGER trigger_update_newsletter_subscriptions_updated_at BEFORE UPDATE ON public.newsletter_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =================================================================
-- RLS Policies
-- =================================================================

-- Policies for anonymous_cart_items
DROP POLICY IF EXISTS "Allow anonymous access to own cart items" ON "public"."anonymous_cart_items";
CREATE POLICY "Allow service role full access to anonymous_cart_items" ON "public"."anonymous_cart_items" AS permissive FOR ALL TO public USING ((auth.role() = 'service_role'::text));
CREATE POLICY "Allow access to cart items by session" ON public.anonymous_cart_items FOR ALL USING (cart_id IN (SELECT id FROM public.anonymous_carts WHERE session_id = current_setting('app.current_session_id', true)::TEXT));

-- Policies for anonymous_carts
CREATE POLICY "Allow anonymous access to own cart" ON "public"."anonymous_carts" AS permissive FOR ALL TO public USING ((auth.role() = 'anon'::text));
CREATE POLICY "Allow service role full access to anonymous_carts" ON "public"."anonymous_carts" AS permissive FOR ALL TO public USING ((auth.role() = 'service_role'::text));
CREATE POLICY "Allow public access with session check" ON public.anonymous_carts FOR ALL USING (true);

-- Policies for cart_items
CREATE POLICY "Cart items are viewable by cart owner." ON "public"."cart_items" AS permissive FOR SELECT TO public USING ((EXISTS (SELECT 1 FROM carts WHERE ((carts.id = cart_items.cart_id) AND (carts.user_id = auth.uid())))));
CREATE POLICY "Users can delete cart items from their cart." ON "public"."cart_items" AS permissive FOR DELETE TO public USING ((EXISTS (SELECT 1 FROM carts WHERE ((carts.id = cart_items.cart_id) AND (carts.user_id = auth.uid())))));
CREATE POLICY "Users can insert cart items for their cart." ON "public"."cart_items" AS permissive FOR INSERT TO public WITH CHECK ((EXISTS (SELECT 1 FROM carts WHERE ((carts.id = cart_items.cart_id) AND (carts.user_id = auth.uid())))));
CREATE POLICY "Users can update cart items for their cart." ON "public"."cart_items" AS permissive FOR UPDATE TO public USING ((EXISTS (SELECT 1 FROM carts WHERE ((carts.id = cart_items.cart_id) AND (carts.user_id = auth.uid())))));

-- Policies for carts
CREATE POLICY "Users can create their own cart." ON "public"."carts" AS permissive FOR INSERT TO public WITH CHECK ((auth.uid() = user_id));
CREATE POLICY "Users can update their own cart." ON "public"."carts" AS permissive FOR UPDATE TO public USING ((auth.uid() = user_id));
CREATE POLICY "Users can view their own cart." ON "public"."carts" AS permissive FOR SELECT TO public USING ((auth.uid() = user_id));

-- Policies for order_items
CREATE POLICY "Order items are viewable by order owner." ON "public"."order_items" AS permissive FOR SELECT TO public USING ((EXISTS (SELECT 1 FROM orders WHERE ((orders.id = order_items.order_id) AND (orders.user_id = auth.uid())))));
CREATE POLICY "Users can insert order items for their orders." ON "public"."order_items" AS permissive FOR INSERT TO public WITH CHECK ((EXISTS (SELECT 1 FROM orders WHERE ((orders.id = order_items.order_id) AND (orders.user_id = auth.uid())))));

-- Policies for orders
CREATE POLICY "Users can create orders" ON public.orders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own orders" ON public.orders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Allow anonymous order creation" ON public.orders FOR INSERT WITH CHECK ((anonymous_cart_id IS NOT NULL AND user_id IS NULL));
DROP POLICY IF EXISTS "Users can update their own orders" ON public.orders;
CREATE POLICY "Users can update their own orders" ON public.orders FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Policies for products
CREATE POLICY "Products are viewable by everyone." ON "public"."products" AS permissive FOR SELECT TO public USING (true);

-- Policies for profiles
CREATE POLICY "Public profiles are viewable by everyone." ON "public"."profiles" AS permissive FOR SELECT TO public USING (true);
CREATE POLICY "Users can insert their own profile." ON "public"."profiles" AS permissive FOR INSERT TO public WITH CHECK ((auth.uid() = id));
CREATE POLICY "Users can update their own profile." ON "public"."profiles" AS permissive FOR UPDATE TO public USING ((auth.uid() = id));

-- Policies for experience_tracks
CREATE POLICY "Allow service role full access to experience_tracks" ON public.experience_tracks FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow authenticated access to experience_tracks" ON public.experience_tracks FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow anonymous access to experience_tracks" ON public.experience_tracks FOR INSERT USING (auth.role() = 'anon');

-- Policies for user_sessions
CREATE POLICY "Allow service role full access to user_sessions" ON public.user_sessions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow authenticated access to user_sessions" ON public.user_sessions FOR ALL USING (auth.role() = 'authenticated');

-- Policies for user_journeys
CREATE POLICY "Allow service role full access to user_journeys" ON public.user_journeys FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow authenticated access to user_journeys" ON public.user_journeys FOR ALL USING (auth.role() = 'authenticated');

-- Policies for performance_metrics
CREATE POLICY "Allow service role full access to performance_metrics" ON public.performance_metrics FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow authenticated access to performance_metrics" ON public.performance_metrics FOR ALL USING (auth.role() = 'authenticated');

-- Policies for addresses
CREATE POLICY "Users can view their own addresses" ON public.addresses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own addresses" ON public.addresses FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own addresses" ON public.addresses FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own addresses" ON public.addresses FOR DELETE USING (auth.uid() = user_id);

-- Policies for reviews
CREATE POLICY "Reviews are public" ON public.reviews FOR SELECT USING (true);
CREATE POLICY "Users can insert their own reviews" ON public.reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own reviews" ON public.reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own reviews" ON public.reviews FOR DELETE USING (auth.uid() = user_id);

-- Policies for newsletter_subscriptions
CREATE POLICY "Public can subscribe to newsletter" ON public.newsletter_subscriptions FOR INSERT WITH CHECK (true);
CREATE POLICY "Service roles can manage subscriptions" ON public.newsletter_subscriptions FOR ALL USING (auth.role() = 'service_role');

-- Policies for order_status_history
CREATE POLICY "Order status history is viewable by order owner" ON public.order_status_history FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.orders o WHERE o.id = order_status_history.order_id AND o.user_id = auth.uid())
);
CREATE POLICY "Service role can manage order status history" ON public.order_status_history FOR ALL USING (auth.role() = 'service_role');

-- =================================================================
-- Comments
-- =================================================================
COMMENT ON TABLE public.anonymous_carts IS 'Stores anonymous shopping carts for users who are not logged in';
COMMENT ON COLUMN public.anonymous_carts.status IS 'Status of the cart: active, abandoned, converted, or expired';
COMMENT ON COLUMN public.anonymous_carts.utm_source IS 'UTM source parameter for tracking marketing campaigns';
COMMENT ON COLUMN public.anonymous_carts.utm_medium IS 'UTM medium parameter for tracking marketing campaigns';
COMMENT ON COLUMN public.anonymous_carts.utm_campaign IS 'UTM campaign parameter for tracking marketing campaigns';
COMMENT ON FUNCTION public.mark_abandoned_carts(INTEGER) IS 'Marks carts as abandoned after a specified period of inactivity (default 30 minutes)';
COMMENT ON FUNCTION public.cleanup_expired_carts() IS 'Removes expired carts from the database. Replaces cleanup_expired_anonymous_carts.';
COMMENT ON FUNCTION public.migrate_anonymous_to_user_cart(TEXT, UUID) IS 'Transfers an anonymous cart to a user account when they log in';
COMMENT ON FUNCTION public.get_cart_by_session(TEXT) IS 'Retrieves cart summary by session ID';
COMMENT ON FUNCTION public.update_cart_totals(UUID) IS 'Updates the item count and total value for a cart';
COMMENT ON TABLE public.experience_tracks IS 'Detailed tracking of user interactions and behavior';
COMMENT ON TABLE public.user_sessions IS 'Session-level aggregated data for user visits';
COMMENT ON TABLE public.user_journeys IS 'User journey and funnel tracking for conversion analysis';
COMMENT ON TABLE public.performance_metrics IS 'Core Web Vitals and performance metrics tracking';
COMMENT ON FUNCTION update_session_stats() IS 'Automatically updates session statistics when experience tracks are added';
COMMENT ON FUNCTION mark_bounce_sessions() IS 'Identifies and marks bounce sessions based on behavior';
COMMENT ON FUNCTION calculate_funnel_conversion(TEXT, TIMESTAMPTZ, TIMESTAMPTZ) IS 'Calculates conversion rates for user journey funnels';
COMMENT ON FUNCTION get_user_behavior_insights(TIMESTAMPTZ, TIMESTAMPTZ) IS 'Provides behavioral insights with period-over-period comparison';
COMMENT ON FUNCTION cleanup_old_experience_data() IS 'Cleans up old tracking data to manage database size';
COMMENT ON COLUMN public.orders.anonymous_cart_id IS 'Reference to the anonymous cart for guest checkouts';
COMMENT ON CONSTRAINT orders_user_or_anonymous_check ON public.orders IS 'Ensures that either user_id or anonymous_cart_id is provided';
COMMENT ON FUNCTION public.create_anonymous_order IS 'Creates an order from an anonymous cart for guest checkouts';
COMMENT ON FUNCTION public.get_order_with_cart IS 'Retrieves order details with associated cart information';
COMMENT ON TABLE public.addresses IS 'Stores shipping and billing addresses for users.';
COMMENT ON TABLE public.reviews IS 'Stores customer reviews for products.';
COMMENT ON TABLE public.newsletter_subscriptions IS 'Stores email addresses for newsletter subscribers.';
COMMENT ON TABLE public.order_status_history IS 'Tracks changes to order status over time.';
```

### User:
```sql
-- Combined Schema for Supabase Project: originz
-- Generated from migration files
-- Updated with critical fixes and optimizations
-- =================================================================
-- Extensions
-- =================================================================
create extension IF not exists "uuid-ossp";

create extension IF not exists "pg_cron";

-- =================================================================
-- Tables
-- =================================================================
-- anon cart items
create table if not exists "public"."anonymous_cart_items" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "cart_id" uuid,
  "product_id" uuid not null, -- Changed from TEXT to UUID
  "variant_id" uuid, -- Changed from TEXT to UUID
  "product_title" text,
  "product_image" text,
  "price" numeric(10, 2) not null,
  "quantity" integer not null,
  "added_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_cart_items" ENABLE row LEVEL SECURITY;

-- anon carts
create table if not exists "public"."anonymous_carts" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "session_id" text not null,
  "expires_at" timestamp with time zone not null default (now() + '7 days'::interval),
  "email" text,
  "phone" text,
  "cart_data" jsonb default '{}'::jsonb,
  "total_value" numeric(10, 2) default 0,
  "item_count" integer default 0,
  "utm_source" text,
  "utm_medium" text,
  "utm_campaign" text,
  "referrer" text,
  "user_agent" text,
  "ip_address" text,
  "status" text default 'active'::text,
  "created_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_carts" ENABLE row LEVEL SECURITY;

-- cart items
create table if not exists "public"."cart_items" (
  "id" uuid not null default gen_random_uuid (),
  "cart_id" uuid,
  "product_id" uuid,
  "variant_id" uuid,
  "quantity" integer not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."cart_items" ENABLE row LEVEL SECURITY;

-- carts
create table if not exists "public"."carts" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."carts" ENABLE row LEVEL SECURITY;

-- order items
create table if not exists "public"."order_items" (
  "id" uuid not null default gen_random_uuid (),
  "order_id" uuid,
  "product_id" uuid,
  "variant_id" uuid,
  "quantity" integer not null,
  "price" numeric(10, 2) not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now() -- Added missing timestamp
);

alter table "public"."order_items" ENABLE row LEVEL SECURITY;

-- orders
create table if not exists "public"."orders" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "status" text not null default 'Pending'::text,
  "total" numeric(10, 2) not null,
  "shipping_address" jsonb,
  "billing_address" jsonb,
  "anonymous_cart_id" UUID,
  "payment_method" TEXT -- Added missing column
);

alter table "public"."orders" ENABLE row LEVEL SECURITY;

-- products
create table if not exists "public"."products" (
  "id" uuid not null default gen_random_uuid (),
  "title" text not null,
  "handle" text not null,
  "description" text,
  "price" numeric(10, 2) not null,
  "compare_at_price" numeric(10, 2),
  "images" jsonb not null default '[]'::jsonb,
  "category" text,
  "in_stock" boolean not null default true,
  "rating" numeric(2, 1) not null default 0.0,
  "review_count" integer not null default 0,
  "tags" text[] not null default '{}'::text[],
  "vendor" text,
  "variants" jsonb not null default '[]'::jsonb,
  "options" jsonb not null default '[]'::jsonb,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
  -- "deleted_at" timestamp with time zone -- Uncomment for soft delete support
);

alter table "public"."products" ENABLE row LEVEL SECURITY;

-- profiles
create table if not exists "public"."profiles" (
  "id" uuid not null,
  "full_name" text,
  "avatar_url" text,
  "billing_address" jsonb,
  "shipping_address" jsonb,
  "updated_at" timestamp with time zone default now()
);

alter table "public"."profiles" ENABLE row LEVEL SECURITY;

-- experience_tracks
create table if not exists public.experience_tracks (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  user_id UUID,
  anonymous_id TEXT,
  event_type TEXT not null check (
    event_type in (
      'page_view',
      'click',
      'scroll',
      'form_interaction',
      'product_view',
      'add_to_cart',
      'search',
      'filter',
      'sort',
      'hover',
      'video_interaction',
      'image_interaction',
      'checkout_step',
      'error',
      'performance'
    )
  ),
  event_name TEXT not null,
  page_url TEXT not null,
  page_title TEXT,
  element_selector TEXT,
  element_text TEXT,
  element_position JSONB,
  interaction_data JSONB default '{}',
  custom_properties JSONB default '{}',
  user_agent TEXT,
  viewport_width INTEGER,
  viewport_height INTEGER,
  screen_width INTEGER,
  screen_height INTEGER,
  device_type TEXT,
  browser_name TEXT,
  browser_version TEXT,
  os_name TEXT,
  os_version TEXT,
  page_load_time INTEGER,
  time_on_page INTEGER,
  scroll_depth INTEGER,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  timezone TEXT,
  client_timestamp TIMESTAMPTZ,
  server_timestamp TIMESTAMPTZ default NOW(),
  created_at TIMESTAMPTZ default NOW()
);

alter table public.experience_tracks ENABLE row LEVEL SECURITY;

-- user_sessions
create table if not exists public.user_sessions (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT unique not null,
  user_id UUID,
  anonymous_id TEXT,
  started_at TIMESTAMPTZ default NOW(),
  ended_at TIMESTAMPTZ,
  duration INTEGER,
  page_views INTEGER default 0,
  interactions INTEGER default 0,
  entry_url TEXT,
  entry_page_title TEXT,
  exit_url TEXT,
  exit_page_title TEXT,
  user_agent TEXT,
  device_type TEXT,
  browser_name TEXT,
  os_name TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  bounce BOOLEAN default false,
  converted BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.user_sessions ENABLE row LEVEL SECURITY;

-- user_journeys
create table if not exists public.user_journeys (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID,
  anonymous_id TEXT,
  session_id TEXT,
  journey_type TEXT not null check (
    journey_type in (
      'product_discovery',
      'purchase_funnel',
      'onboarding',
      'support',
      'content_engagement'
    )
  ),
  journey_step TEXT not null,
  step_order INTEGER not null,
  page_url TEXT,
  action_taken TEXT,
  time_spent INTEGER,
  completed BOOLEAN default false,
  dropped_off BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  properties JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.user_journeys ENABLE row LEVEL SECURITY;

-- performance_metrics
create table if not exists public.performance_metrics (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  page_url TEXT not null,
  lcp DECIMAL(8, 2),
  fid DECIMAL(8, 2),
  cls DECIMAL(6, 4),
  fcp DECIMAL(8, 2),
  ttfb DECIMAL(8, 2),
  dns_lookup_time INTEGER,
  tcp_connect_time INTEGER,
  tls_setup_time INTEGER,
  request_time INTEGER,
  response_time INTEGER,
  dom_processing_time INTEGER,
  load_event_time INTEGER,
  custom_metrics JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.performance_metrics ENABLE row LEVEL SECURITY;

-- addresses
create table if not exists public.addresses (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID not null references auth.users (id) on delete CASCADE,
  type TEXT not null check (type in ('shipping', 'billing')),
  first_name TEXT not null,
  last_name TEXT not null,
  address TEXT not null,
  city TEXT not null,
  postal_code TEXT not null,
  country TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.addresses ENABLE row LEVEL SECURITY;

-- reviews
create table if not exists public.reviews (
  id UUID primary key default uuid_generate_v4 (),
  product_id UUID not null references public.products (id) on delete CASCADE,
  user_id UUID not null references auth.users (id) on delete CASCADE,
  rating INTEGER not null check (
    rating >= 1
    and rating <= 5
  ),
  comment TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  unique (product_id, user_id)
);

alter table public.reviews ENABLE row LEVEL SECURITY;

-- newsletter_subscriptions
create table if not exists public.newsletter_subscriptions (
  id UUID primary key default uuid_generate_v4 (),
  email TEXT not null unique,
  subscribed_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW() -- Added missing timestamp
);

alter table public.newsletter_subscriptions ENABLE row LEVEL SECURITY;

-- order_status_history (NEW TABLE)
create table if not exists public.order_status_history (
  id UUID primary key default uuid_generate_v4 (),
  order_id UUID not null references public.orders (id) on delete CASCADE,
  old_status TEXT,
  new_status TEXT not null,
  changed_by UUID references auth.users (id),
  notes TEXT,
  created_at TIMESTAMPTZ default NOW()
);

-- =================================================================
-- Indexes
-- =================================================================
create unique INDEX IF not exists anonymous_cart_items_pkey on public.anonymous_cart_items using btree (id);

create unique INDEX IF not exists anonymous_carts_pkey on public.anonymous_carts using btree (id);

create unique INDEX IF not exists anonymous_carts_session_id_key on public.anonymous_carts using btree (session_id);

create unique INDEX IF not exists cart_items_pkey on public.cart_items using btree (id);

create unique INDEX IF not exists carts_pkey on public.carts using btree (id);

create unique INDEX IF not exists carts_user_id_key on public.carts (user_id);

-- Added unique constraint
create index IF not exists idx_anonymous_cart_items_cart_id on public.anonymous_cart_items using btree (cart_id);

create index IF not exists idx_anonymous_cart_items_product_id on public.anonymous_cart_items using btree (product_id);

create index IF not exists idx_anonymous_cart_items_variant_id on public.anonymous_cart_items using btree (variant_id)
where
  (variant_id is not null);

create index IF not exists idx_anonymous_carts_email on public.anonymous_carts using btree (email)
where
  (email is not null);

create index IF not exists idx_anonymous_carts_expires_at on public.anonymous_carts using btree (expires_at);

create index IF not exists idx_anonymous_carts_session_id on public.anonymous_carts using btree (session_id);

create index IF not exists idx_anonymous_carts_status on public.anonymous_carts using btree (status);

create index IF not exists idx_anonymous_carts_utm_source on public.anonymous_carts using btree (utm_source)
where
  (utm_source is not null);

create unique INDEX IF not exists order_items_pkey on public.order_items using btree (id);

create unique INDEX IF not exists orders_pkey on public.orders using btree (id);

create unique INDEX IF not exists products_handle_key on public.products using btree (handle);

create unique INDEX IF not exists products_pkey on public.products using btree (id);

create unique INDEX IF not exists profiles_pkey on public.profiles using btree (id);

-- Composite indexes for performance
create index IF not exists idx_anonymous_carts_status_created_at on public.anonymous_carts (status, created_at);

create index IF not exists idx_products_category_in_stock on public.products (category, in_stock)
where
  in_stock = true;

create index IF not exists idx_orders_user_status on public.orders (user_id, status)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_session_event on public.experience_tracks (session_id, event_type, created_at);

-- GIN indexes for JSONB columns
create index IF not exists idx_products_tags_gin on public.products using GIN (tags);

create index IF not exists idx_products_variants_gin on public.products using GIN (variants);

create index IF not exists idx_anonymous_carts_cart_data_gin on public.anonymous_carts using GIN (cart_data);

create index IF not exists idx_experience_tracks_properties_gin on public.experience_tracks using GIN (custom_properties);

-- Missing foreign key indexes
create index IF not exists idx_cart_items_cart_id on public.cart_items (cart_id);

create index IF not exists idx_cart_items_product_id on public.cart_items (product_id);

create index IF not exists idx_cart_items_variant_id on public.cart_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_order_items_order_id on public.order_items (order_id);

create index IF not exists idx_order_items_product_id on public.order_items (product_id);

create index IF not exists idx_order_items_variant_id on public.order_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_carts_user_id on public.carts (user_id);

-- Unique constraint for cart items
create unique INDEX IF not exists cart_items_cart_product_variant_key on public.cart_items (
  cart_id,
  product_id,
  COALESCE(
    variant_id,
    '00000000-0000-0000-0000-000000000000'::UUID
  )
);

-- Additional indexes from original
create index IF not exists idx_experience_tracks_session_id on public.experience_tracks (session_id);

create index IF not exists idx_experience_tracks_user_id on public.experience_tracks (user_id)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_anonymous_id on public.experience_tracks (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_experience_tracks_event_type on public.experience_tracks (event_type);

create index IF not exists idx_experience_tracks_page_url on public.experience_tracks (page_url);

create index IF not exists idx_experience_tracks_created_at on public.experience_tracks (created_at);

create index IF not exists idx_user_sessions_session_id on public.user_sessions (session_id);

create index IF not exists idx_user_sessions_user_id on public.user_sessions (user_id)
where
  user_id is not null;

create index IF not exists idx_user_sessions_started_at on public.user_sessions (started_at);

create index IF not exists idx_user_journeys_user_id on public.user_journeys (user_id)
where
  user_id is not null;

create index IF not exists idx_user_journeys_anonymous_id on public.user_journeys (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_user_journeys_journey_type on public.user_journeys (journey_type);

create index IF not exists idx_user_journeys_session_id on public.user_journeys (session_id);

create index IF not exists idx_performance_metrics_session_id on public.performance_metrics (session_id);

create index IF not exists idx_performance_metrics_page_url on public.performance_metrics (page_url);

create index IF not exists idx_performance_metrics_created_at on public.performance_metrics (created_at);

create index IF not exists idx_anonymous_carts_updated_at on public.anonymous_carts (updated_at);

create index IF not exists idx_orders_anonymous_cart_id on public.orders (anonymous_cart_id)
where
  anonymous_cart_id is not null;

create index IF not exists idx_orders_status on public.orders (status);

create index IF not exists idx_orders_created_at on public.orders (created_at);

create index IF not exists idx_orders_user_id on public.orders (user_id)
where
  user_id is not null;

create index IF not exists idx_addresses_user_id on public.addresses (user_id);

create index IF not exists idx_reviews_product_id on public.reviews (product_id);

create index IF not exists idx_reviews_user_id on public.reviews (user_id);

create index IF not exists idx_order_status_history_order_id on public.order_status_history (order_id);

-- Soft delete index (uncomment if using soft delete)
-- CREATE INDEX IF NOT EXISTS idx_products_deleted_at ON public.products(deleted_at) WHERE deleted_at IS NULL;
-- =================================================================
-- Primary Keys & Foreign Keys & Constraints
-- =================================================================
-- Primary Keys
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_pkey" primary key using INDEX "anonymous_cart_items_pkey";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_pkey" primary key using INDEX "anonymous_carts_pkey";

alter table "public"."cart_items"
add constraint "cart_items_pkey" primary key using INDEX "cart_items_pkey";

alter table "public"."carts"
add constraint "carts_pkey" primary key using INDEX "carts_pkey";

alter table "public"."order_items"
add constraint "order_items_pkey" primary key using INDEX "order_items_pkey";

alter table "public"."orders"
add constraint "orders_pkey" primary key using INDEX "orders_pkey";

alter table "public"."products"
add constraint "products_pkey" primary key using INDEX "products_pkey";

alter table "public"."profiles"
add constraint "profiles_pkey" primary key using INDEX "profiles_pkey";

-- Foreign Keys & Constraints
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_cart_id_fkey" foreign KEY (cart_id) references anonymous_carts (id) on delete CASCADE;

alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_quantity_check" check ((quantity > 0));

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_session_id_key" unique using INDEX "anonymous_carts_session_id_key";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_status_check" check (
  (
    (
      status = any (
        array[
          'active'::text,
          'abandoned'::text,
          'converted'::text,
          'expired'::text
        ]
      )
    )
  )
);

alter table "public"."cart_items"
add constraint "cart_items_cart_id_fkey" foreign KEY (cart_id) references carts (id) on delete CASCADE;

alter table "public"."cart_items"
add constraint "cart_items_product_id_fkey" foreign KEY (product_id) references products (id) on delete CASCADE;

alter table "public"."cart_items"
add constraint "cart_items_variant_id_fkey" foreign KEY (variant_id) references products (id) on delete CASCADE;

-- Added missing constraint
alter table "public"."carts"
add constraint "carts_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."order_items"
add constraint "order_items_order_id_fkey" foreign KEY (order_id) references orders (id) on delete CASCADE;

alter table "public"."order_items"
add constraint "order_items_product_id_fkey" foreign KEY (product_id) references products (id) on delete set null;

alter table "public"."orders"
alter column user_id
drop not null;

alter table "public"."orders"
add constraint "orders_anonymous_cart_id_fkey" foreign KEY (anonymous_cart_id) references public.anonymous_carts (id) on delete set null deferrable initially DEFERRED;

alter table "public"."orders"
add constraint "orders_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."orders"
add constraint orders_user_or_anonymous_check check (
  (
    (user_id is not null)
    or (anonymous_cart_id is not null)
  )
);

alter table "public"."products"
add constraint "products_handle_key" unique using INDEX "products_handle_key";

alter table "public"."profiles"
add constraint "profiles_id_fkey" foreign KEY (id) references auth.users (id) on delete CASCADE;

-- Added foreign key for anonymous_cart_items
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_product_id_fkey" foreign KEY (product_id) references products (id) on delete CASCADE;

-- Check constraints for data integrity
alter table public.products
add constraint products_price_positive check (price > 0),
add constraint products_compare_at_price_positive check (
  compare_at_price is null
  or compare_at_price > 0
),
add constraint products_rating_range check (
  rating >= 0
  and rating <= 5
);

alter table public.order_items
add constraint order_items_price_positive check (price >= 0),
add constraint order_items_quantity_positive check (quantity > 0);

-- Email validation constraints
alter table public.anonymous_carts
add constraint anonymous_carts_email_valid check (
  email is null
  or email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

alter table public.newsletter_subscriptions
add constraint newsletter_subscriptions_email_valid check (
  email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

-- =================================================================
-- Functions
-- =================================================================
create or replace function public.update_updated_at_column () RETURNS trigger LANGUAGE plpgsql as $function$ BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 $function$;

create or replace function public.get_cart_analytics (
  p_start_date timestamp with time zone,
  p_end_date timestamp with time zone
) RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            DATE(created_at) AS date,
            COUNT(*) FILTER (WHERE status = 'active') AS active_carts,
            COUNT(*) FILTER (WHERE status = 'abandoned') AS abandoned_carts,
            COUNT(*) FILTER (WHERE status = 'converted') AS converted_carts,
            AVG(total_value) FILTER (WHERE status = 'converted') AS avg_cart_value,
            AVG(item_count) FILTER (WHERE status = 'converted') AS avg_items_per_cart
        FROM public.anonymous_carts
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(created_at)
    )
    SELECT 
        ds.date,
        COALESCE(ds.active_carts, 0)::INTEGER,
        COALESCE(ds.abandoned_carts, 0)::INTEGER,
        COALESCE(ds.converted_carts, 0)::INTEGER,
        COALESCE(ds.avg_cart_value, 0)::NUMERIC(10,2),
        COALESCE(ds.avg_items_per_cart, 0)::NUMERIC(10,2)
    FROM daily_stats ds
    ORDER BY ds.date;
END;
 $function$;

create or replace function public.get_cart_analytics () RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY SELECT * FROM public.get_cart_analytics(
        (NOW() - INTERVAL '30 days'),
        NOW()
    );
END;
 $function$;

create or replace function public.mark_abandoned_carts (abandonment_minutes INTEGER default 30) RETURNS INTEGER LANGUAGE plpgsql as $function$ DECLARE
    updated_count INTEGER;
BEGIN
    WITH abandoned_carts AS (
        UPDATE public.anonymous_carts
        SET status = 'abandoned',
            updated_at = NOW()
        WHERE status = 'active'
        AND updated_at < (NOW() - (abandonment_minutes * INTERVAL '1 minute'))
        RETURNING 1
    )
    SELECT COUNT(*) INTO updated_count FROM abandoned_carts;
    
    RETURN updated_count;
END;
 $function$;

create or replace function public.update_cart_totals (p_cart_id UUID) RETURNS VOID as $$ BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.trigger_update_cart_totals () RETURNS TRIGGER as $$ BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM public.update_cart_totals(OLD.cart_id);
        RETURN OLD;
    ELSE
        PERFORM public.update_cart_totals(NEW.cart_id);
        RETURN NEW;
    END IF;
END;
 $$ LANGUAGE plpgsql;

create or replace function update_session_stats () RETURNS TRIGGER as $$ BEGIN
    INSERT INTO public.user_sessions (
        session_id, user_id, anonymous_id, started_at, entry_url, entry_page_title,
        user_agent, device_type, browser_name, os_name,
        utm_source, utm_medium, utm_campaign, referrer_url,
        ip_address, country_code, city, page_views, interactions
    )
    VALUES (
        NEW.session_id, NEW.user_id, NEW.anonymous_id, NEW.created_at, NEW.page_url, NEW.page_title,
        NEW.user_agent, NEW.device_type, NEW.browser_name, NEW.os_name,
        NEW.utm_source, NEW.utm_medium, NEW.utm_campaign, NEW.referrer_url,
        NEW.ip_address, NEW.country_code, NEW.city, 
        CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END
    )
    ON CONFLICT (session_id) DO UPDATE SET
        user_id = COALESCE(NEW.user_id, user_sessions.user_id),
        ended_at = NEW.created_at,
        exit_url = NEW.page_url,
        exit_page_title = NEW.page_title,
        page_views = user_sessions.page_views + CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        interactions = user_sessions.interactions + CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END,
        duration = EXTRACT(EPOCH FROM (NEW.created_at - user_sessions.started_at))::INTEGER,
        updated_at = NOW();

    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

create or replace function mark_bounce_sessions () RETURNS INTEGER as $$ DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.user_sessions 
    SET bounce = TRUE, updated_at = NOW()
    WHERE page_views <= 1 
      AND duration < 30 
      AND bounce = FALSE
      AND ended_at < (NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function calculate_funnel_conversion (
  p_journey_type TEXT,
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '30 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  step TEXT,
  step_order INTEGER,
  users BIGINT,
  conversion_rate DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH funnel_steps AS (
        SELECT 
            journey_step,
            step_order,
            COUNT(DISTINCT COALESCE(user_id::TEXT, anonymous_id)) as step_users
        FROM public.user_journeys
        WHERE journey_type = p_journey_type
          AND created_at BETWEEN p_start_date AND p_end_date
        GROUP BY journey_step, step_order
        ORDER BY step_order
    ),
    first_step AS (
        SELECT step_users as first_step_users
        FROM funnel_steps
        ORDER BY step_order
        LIMIT 1
    )
    SELECT 
        fs.journey_step,
        fs.step_order,
        fs.step_users,
        CASE 
            WHEN fst.first_step_users > 0 THEN 
                ROUND((fs.step_users::DECIMAL / fst.first_step_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    CROSS JOIN first_step fst
    ORDER BY fs.step_order;
END;
 $$ LANGUAGE plpgsql;

create or replace function get_user_behavior_insights (
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '7 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  metric_name TEXT,
  metric_value DECIMAL,
  metric_unit TEXT,
  comparison_period_value DECIMAL,
  change_percentage DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN 
            p_start_date - (p_end_date - p_start_date) AND 
            p_start_date
    )
    SELECT 
        'Total Sessions'::TEXT,
        cp.total_sessions::DECIMAL,
        'count'::TEXT,
        pp.total_sessions::DECIMAL,
        CASE WHEN pp.total_sessions > 0 THEN ROUND(((cp.total_sessions - pp.total_sessions)::DECIMAL / pp.total_sessions) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Time on Page'::TEXT,
        ROUND(cp.avg_time_on_page, 2),
        'seconds'::TEXT,
        ROUND(pp.avg_time_on_page, 2),
        CASE WHEN pp.avg_time_on_page > 0 THEN ROUND(((cp.avg_time_on_page - pp.avg_time_on_page) / pp.avg_time_on_page) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Scroll Depth'::TEXT,
        ROUND(cp.avg_scroll_depth, 2),
        'percentage'::TEXT,
        ROUND(pp.avg_scroll_depth, 2),
        CASE WHEN pp.avg_scroll_depth > 0 THEN ROUND(((cp.avg_scroll_depth - pp.avg_scroll_depth) / pp.avg_scroll_depth) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
 $$ LANGUAGE plpgsql;

create or replace function cleanup_old_experience_data () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.experience_tracks WHERE created_at < (NOW() - INTERVAL '90 days');
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM public.user_sessions WHERE created_at < (NOW() - INTERVAL '90 days');
    DELETE FROM public.performance_metrics WHERE created_at < (NOW() - INTERVAL '30 days');
    DELETE FROM public.user_journeys WHERE created_at < (NOW() - INTERVAL '90 days');
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.cleanup_expired_carts () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.anonymous_carts
        WHERE expires_at < NOW()
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.migrate_anonymous_to_user_cart (p_session_id TEXT, p_user_id UUID) RETURNS UUID as $$ DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;
    
    SELECT id INTO v_anonymous_cart_id
    FROM public.anonymous_carts
    WHERE session_id = p_session_id
    AND status = 'active';
    
    IF v_anonymous_cart_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    INSERT INTO public.carts (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id)
    DO UPDATE SET updated_at = NOW()
    RETURNING id INTO v_cart_id;
    
    INSERT INTO public.cart_items (cart_id, product_id, variant_id, quantity)
    SELECT v_cart_id, product_id, variant_id, quantity
    FROM public.anonymous_cart_items
    WHERE cart_id = v_anonymous_cart_id
    ON CONFLICT (cart_id, product_id, variant_id) 
    DO UPDATE SET 
        quantity = cart_items.quantity + EXCLUDED.quantity,
        updated_at = NOW();
    
    UPDATE public.anonymous_carts
    SET status = 'converted',
        updated_at = NOW()
    WHERE id = v_anonymous_cart_id;
    
    RETURN v_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.get_cart_by_session (p_session_id TEXT) RETURNS table (
  cart_id UUID,
  session_id TEXT,
  status TEXT,
  item_count INTEGER,
  total_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) as $$ BEGIN
    RETURN QUERY
    SELECT 
        ac.id AS cart_id,
        ac.session_id,
        ac.status,
        COALESCE(SUM(aci.quantity), 0)::INTEGER AS item_count,
        COALESCE(SUM(aci.price * aci.quantity), 0)::DECIMAL(10,2) AS total_value,
        ac.created_at,
        ac.updated_at
    FROM public.anonymous_carts ac
    LEFT JOIN public.anonymous_cart_items aci ON ac.id = aci.cart_id
    WHERE ac.session_id = p_session_id
    GROUP BY ac.id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.schedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN PERFORM cron.schedule('mark-abandoned-carts', '0 * * * *', 'SELECT public.mark_abandoned_carts(30)'); PERFORM cron.schedule('cleanup-expired-carts', '0 3 * * *', 'SELECT public.cleanup_expired_carts()'); END; $$ LANGUAGE plpgsql;

create or replace function public.unschedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN
    PERFORM cron.unschedule('mark-abandoned-carts');
    PERFORM cron.unschedule('cleanup-expired-carts');
END;
 $$ LANGUAGE plpgsql;

create or replace function public.recover_abandoned_cart (p_session_id TEXT) RETURNS BOOLEAN as $$ DECLARE
    v_updated_rows INTEGER;
BEGIN
    UPDATE public.anonymous_carts
    SET status = 'active',
        updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'abandoned';
    
    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
    RETURN v_updated_rows > 0;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.create_anonymous_order (
  p_anonymous_cart_id UUID,
  p_shipping_address JSONB,
  p_billing_address JSONB,
  p_payment_method TEXT,
  p_status TEXT default 'pending'
) RETURNS UUID as $$ DECLARE
    v_order_id UUID;
    v_cart_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_anonymous_cart_id IS NULL OR p_shipping_address IS NULL OR p_payment_method IS NULL THEN
        RAISE EXCEPTION 'Cart ID, shipping address, and payment method are required';
    END IF;
    
    SELECT EXISTS (
        SELECT 1
        FROM public.anonymous_carts
        WHERE id = p_anonymous_cart_id AND status = 'active'
    ) INTO v_cart_exists;

    IF NOT v_cart_exists THEN
        RAISE EXCEPTION 'Invalid or inactive anonymous cart';
    END IF;

    INSERT INTO public.orders (anonymous_cart_id, status, shipping_address, billing_address, payment_method, created_at, updated_at, total)
    VALUES (p_anonymous_cart_id, p_status, p_shipping_address, p_billing_address, p_payment_method, NOW(), NOW(), (SELECT total_value FROM public.anonymous_carts WHERE id = p_anonymous_cart_id))
    RETURNING id INTO v_order_id;

    UPDATE public.anonymous_carts
    SET status = 'converted', updated_at = NOW()
    WHERE id = p_anonymous_cart_id;

    RETURN v_order_id;
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

create or replace function public.get_order_with_cart (p_order_id UUID) RETURNS JSONB as $$ DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'order_id', o.id,
        'status', o.status,
        'created_at', o.created_at,
        'updated_at', o.updated_at,
        'shipping_address', o.shipping_address,
        'billing_address', o.billing_address,
        'payment_method', o.payment_method,
        'is_guest_order', o.user_id IS NULL,
        'cart', CASE
            WHEN o.anonymous_cart_id IS NOT NULL THEN (
                SELECT jsonb_build_object(
                    'cart_id', ac.id,
                    'session_id', ac.session_id,
                    'created_at', ac.created_at,
                    'items', COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'product_id', aci.product_id,
                            'variant_id', aci.variant_id,
                            'product_title', aci.product_title,
                            'product_image', aci.product_image,
                            'price', aci.price,
                            'quantity', aci.quantity
                        ))
                        FROM public.anonymous_cart_items aci
                        WHERE aci.cart_id = ac.id
                    ), '[]'::jsonb)
                )
                FROM public.anonymous_carts ac
                WHERE ac.id = o.anonymous_cart_id
            )
            ELSE NULL
        END,
        'user', CASE
            WHEN o.user_id IS NOT NULL THEN (
                SELECT jsonb_build_object('id', u.id, 'email', u.email)
                FROM auth.users u
                WHERE u.id = o.user_id
            )
            ELSE NULL
        END
    ) INTO v_result
    FROM public.orders o
    WHERE o.id = p_order_id;
    RETURN v_result;
END;
 $$ LANGUAGE plpgsql STABLE;

create or replace function public.sync_order_cart_status () RETURNS TRIGGER as $$ BEGIN
    IF NEW.status = 'converted' AND OLD.status != 'converted' THEN
        UPDATE public.orders
        SET status = 'processing', updated_at = NOW()
        WHERE anonymous_cart_id = NEW.id AND status = 'pending';
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

-- Rate limiting function
create or replace function check_rate_limit (p_ip_address INET) RETURNS BOOLEAN as $$ DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

-- =================================================================
-- Triggers
-- =================================================================
drop trigger IF exists trigger_update_anonymous_cart_items_updated_at on public.anonymous_cart_items;

create trigger trigger_update_anonymous_cart_items_updated_at BEFORE
update on public.anonymous_cart_items for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_cart_totals_on_delete on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_delete
after DELETE on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_insert on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_insert
after INSERT on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_update on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_update
after
update on public.anonymous_cart_items for EACH row when (
  OLD.quantity is distinct from NEW.quantity
  or OLD.price is distinct from NEW.price
)
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_anonymous_carts_updated_at on public.anonymous_carts;

create trigger trigger_update_anonymous_carts_updated_at BEFORE
update on public.anonymous_carts for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_session_stats on public.experience_tracks;

create trigger trigger_update_session_stats
after INSERT on public.experience_tracks for EACH row
execute FUNCTION update_session_stats ();

drop trigger IF exists trg_sync_order_cart_status on public.anonymous_carts;

create trigger trg_sync_order_cart_status
after
update OF status on public.anonymous_carts for EACH row when (OLD.status is distinct from NEW.status)
execute FUNCTION public.sync_order_cart_status ();

-- Trigger for order_items updated_at
drop trigger IF exists trigger_update_order_items_updated_at on public.order_items;

create trigger trigger_update_order_items_updated_at BEFORE
update on public.order_items for EACH row
execute FUNCTION update_updated_at_column ();

-- Trigger for newsletter_subscriptions updated_at
drop trigger IF exists trigger_update_newsletter_subscriptions_updated_at on public.newsletter_subscriptions;

create trigger trigger_update_newsletter_subscriptions_updated_at BEFORE
update on public.newsletter_subscriptions for EACH row
execute FUNCTION update_updated_at_column ();

-- =================================================================
-- RLS Policies
-- =================================================================
-- Policies for anonymous_cart_items
drop policy IF exists "Allow anonymous access to own cart items" on "public"."anonymous_cart_items";

create policy "Allow service role full access to anonymous_cart_items" on "public"."anonymous_cart_items" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow access to cart items by session" on public.anonymous_cart_items for all using (
  cart_id in (
    select
      id
    from
      public.anonymous_carts
    where
      session_id = current_setting('app.current_session_id', true)::TEXT
  )
);

-- Policies for anonymous_carts
create policy "Allow anonymous access to own cart" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'anon'::text));

create policy "Allow service role full access to anonymous_carts" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow public access with session check" on public.anonymous_carts for all using (true);

-- Policies for cart_items
create policy "Cart items are viewable by cart owner." on "public"."cart_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can delete cart items from their cart." on "public"."cart_items" as permissive for DELETE to public using (
  (
    exists (
      select
        1
      from
        carts
      where
        (
          (carts.id = cart_items.cart_id)
          and (carts.user_id = auth.uid ())
        )
    )
  )
);

create policy "Users can insert cart items for their cart." on "public"."cart_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can update cart items for their cart." on "public"."cart_items" as permissive
for update
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for carts
create policy "Users can create their own cart." on "public"."carts" as permissive for INSERT to public
with
  check ((auth.uid () = user_id));

create policy "Users can update their own cart." on "public"."carts" as permissive
for update
  to public using ((auth.uid () = user_id));

create policy "Users can view their own cart." on "public"."carts" as permissive for
select
  to public using ((auth.uid () = user_id));

-- Policies for order_items
create policy "Order items are viewable by order owner." on "public"."order_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can insert order items for their orders." on "public"."order_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for orders
create policy "Users can create orders" on public.orders for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can view their own orders" on public.orders for
select
  using (auth.uid () = user_id);

create policy "Allow anonymous order creation" on public.orders for INSERT
with
  check (
    (
      anonymous_cart_id is not null
      and user_id is null
    )
  );

drop policy IF exists "Users can update their own orders" on public.orders;

create policy "Users can update their own orders" on public.orders
for update
  using (auth.uid () = user_id)
with
  check (auth.uid () = user_id);

-- Policies for products
create policy "Products are viewable by everyone." on "public"."products" as permissive for
select
  to public using (true);

-- Policies for profiles
create policy "Public profiles are viewable by everyone." on "public"."profiles" as permissive for
select
  to public using (true);

create policy "Users can insert their own profile." on "public"."profiles" as permissive for INSERT to public
with
  check ((auth.uid () = id));

create policy "Users can update their own profile." on "public"."profiles" as permissive
for update
  to public using ((auth.uid () = id));

-- Policies for experience_tracks
create policy "Allow service role full access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'authenticated');

create policy "Allow anonymous access to experience_tracks" on public.experience_tracks for INSERT using (auth.role () = 'anon');

-- Policies for user_sessions
create policy "Allow service role full access to user_sessions" on public.user_sessions for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_sessions" on public.user_sessions for all using (auth.role () = 'authenticated');

-- Policies for user_journeys
create policy "Allow service role full access to user_journeys" on public.user_journeys for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_journeys" on public.user_journeys for all using (auth.role () = 'authenticated');

-- Policies for performance_metrics
create policy "Allow service role full access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'authenticated');

-- Policies for addresses
create policy "Users can view their own addresses" on public.addresses for
select
  using (auth.uid () = user_id);

create policy "Users can insert their own addresses" on public.addresses for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own addresses" on public.addresses
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own addresses" on public.addresses for DELETE using (auth.uid () = user_id);

-- Policies for reviews
create policy "Reviews are public" on public.reviews for
select
  using (true);

create policy "Users can insert their own reviews" on public.reviews for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own reviews" on public.reviews
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own reviews" on public.reviews for DELETE using (auth.uid () = user_id);

-- Policies for newsletter_subscriptions
create policy "Public can subscribe to newsletter" on public.newsletter_subscriptions for INSERT
with
  check (true);

create policy "Service roles can manage subscriptions" on public.newsletter_subscriptions for all using (auth.role () = 'service_role');

-- Policies for order_status_history
create policy "Order status history is viewable by order owner" on public.order_status_history for
select
  using (
    exists (
      select
        1
      from
        public.orders o
      where
        o.id = order_status_history.order_id
        and o.user_id = auth.uid ()
    )
  );

create policy "Service role can manage order status history" on public.order_status_history for all using (auth.role () = 'service_role');

-- =================================================================
-- Comments
-- =================================================================
COMMENT on table public.anonymous_carts is 'Stores anonymous shopping carts for users who are not logged in';

COMMENT on column public.anonymous_carts.status is 'Status of the cart: active, abandoned, converted, or expired';

COMMENT on column public.anonymous_carts.utm_source is 'UTM source parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_medium is 'UTM medium parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_campaign is 'UTM campaign parameter for tracking marketing campaigns';

COMMENT on FUNCTION public.mark_abandoned_carts (INTEGER) is 'Marks carts as abandoned after a specified period of inactivity (default 30 minutes)';

COMMENT on FUNCTION public.cleanup_expired_carts () is 'Removes expired carts from the database. Replaces cleanup_expired_anonymous_carts.';

COMMENT on FUNCTION public.migrate_anonymous_to_user_cart (TEXT, UUID) is 'Transfers an anonymous cart to a user account when they log in';

COMMENT on FUNCTION public.get_cart_by_session (TEXT) is 'Retrieves cart summary by session ID';

COMMENT on FUNCTION public.update_cart_totals (UUID) is 'Updates the item count and total value for a cart';

COMMENT on table public.experience_tracks is 'Detailed tracking of user interactions and behavior';

COMMENT on table public.user_sessions is 'Session-level aggregated data for user visits';

COMMENT on table public.user_journeys is 'User journey and funnel tracking for conversion analysis';

COMMENT on table public.performance_metrics is 'Core Web Vitals and performance metrics tracking';

COMMENT on FUNCTION update_session_stats () is 'Automatically updates session statistics when experience tracks are added';

COMMENT on FUNCTION mark_bounce_sessions () is 'Identifies and marks bounce sessions based on behavior';

COMMENT on FUNCTION calculate_funnel_conversion (TEXT, TIMESTAMPTZ, TIMESTAMPTZ) is 'Calculates conversion rates for user journey funnels';

COMMENT on FUNCTION get_user_behavior_insights (TIMESTAMPTZ, TIMESTAMPTZ) is 'Provides behavioral insights with period-over-period comparison';

COMMENT on FUNCTION cleanup_old_experience_data () is 'Cleans up old tracking data to manage database size';

COMMENT on column public.orders.anonymous_cart_id is 'Reference to the anonymous cart for guest checkouts';

COMMENT on constraint orders_user_or_anonymous_check on public.orders is 'Ensures that either user_id or anonymous_cart_id is provided';

COMMENT on FUNCTION public.create_anonymous_order is 'Creates an order from an anonymous cart for guest checkouts';

COMMENT on FUNCTION public.get_order_with_cart is 'Retrieves order details with associated cart information';

COMMENT on table public.addresses is 'Stores shipping and billing addresses for users.';

COMMENT on table public.reviews is 'Stores customer reviews for products.';

COMMENT on table public.newsletter_subscriptions is 'Stores email addresses for newsletter subscribers.';

COMMENT on table public.order_status_history is 'Tracks changes to order status over time.';
```

# issues 
- ERROR:  42830: there is no unique constraint matching given keys for referenced table "products"
we don't need products tables because our application getting products from external API
and their id is a number

### Assistant:
I see the issue. The error occurs because you're trying to create foreign key constraints that reference the `products` table, but you don't need this table since your application gets products from an external API with numeric IDs. Let me fix the schema to remove these references and adjust the data types accordingly.

```sql
-- Combined Schema for Supabase Project: originz
-- Generated from migration files
-- Updated with critical fixes and optimizations
-- =================================================================
-- Extensions
-- =================================================================
create extension IF not exists "uuid-ossp";

create extension IF not exists "pg_cron";

-- =================================================================
-- Tables
-- =================================================================
-- anon cart items
create table if not exists "public"."anonymous_cart_items" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "cart_id" uuid,
  "product_id" integer not null, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "product_title" text,
  "product_image" text,
  "price" numeric(10, 2) not null,
  "quantity" integer not null,
  "added_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_cart_items" ENABLE row LEVEL SECURITY;

-- anon carts
create table if not exists "public"."anonymous_carts" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "session_id" text not null,
  "expires_at" timestamp with time zone not null default (now() + '7 days'::interval),
  "email" text,
  "phone" text,
  "cart_data" jsonb default '{}'::jsonb,
  "total_value" numeric(10, 2) default 0,
  "item_count" integer default 0,
  "utm_source" text,
  "utm_medium" text,
  "utm_campaign" text,
  "referrer" text,
  "user_agent" text,
  "ip_address" text,
  "status" text default 'active'::text,
  "created_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_carts" ENABLE row LEVEL SECURITY;

-- cart items
create table if not exists "public"."cart_items" (
  "id" uuid not null default gen_random_uuid (),
  "cart_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."cart_items" ENABLE row LEVEL SECURITY;

-- carts
create table if not exists "public"."carts" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."carts" ENABLE row LEVEL SECURITY;

-- order items
create table if not exists "public"."order_items" (
  "id" uuid not null default gen_random_uuid (),
  "order_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "price" numeric(10, 2) not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now() -- Added missing timestamp
);

alter table "public"."order_items" ENABLE row LEVEL SECURITY;

-- orders
create table if not exists "public"."orders" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "status" text not null default 'Pending'::text,
  "total" numeric(10, 2) not null,
  "shipping_address" jsonb,
  "billing_address" jsonb,
  "anonymous_cart_id" UUID,
  "payment_method" TEXT -- Added missing column
);

alter table "public"."orders" ENABLE row LEVEL SECURITY;

-- profiles
create table if not exists "public"."profiles" (
  "id" uuid not null,
  "full_name" text,
  "avatar_url" text,
  "billing_address" jsonb,
  "shipping_address" jsonb,
  "updated_at" timestamp with time zone default now()
);

alter table "public"."profiles" ENABLE row LEVEL SECURITY;

-- experience_tracks
create table if not exists public.experience_tracks (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  user_id UUID,
  anonymous_id TEXT,
  event_type TEXT not null check (
    event_type in (
      'page_view',
      'click',
      'scroll',
      'form_interaction',
      'product_view',
      'add_to_cart',
      'search',
      'filter',
      'sort',
      'hover',
      'video_interaction',
      'image_interaction',
      'checkout_step',
      'error',
      'performance'
    )
  ),
  event_name TEXT not null,
  page_url TEXT not null,
  page_title TEXT,
  element_selector TEXT,
  element_text TEXT,
  element_position JSONB,
  interaction_data JSONB default '{}',
  custom_properties JSONB default '{}',
  user_agent TEXT,
  viewport_width INTEGER,
  viewport_height INTEGER,
  screen_width INTEGER,
  screen_height INTEGER,
  device_type TEXT,
  browser_name TEXT,
  browser_version TEXT,
  os_name TEXT,
  os_version TEXT,
  page_load_time INTEGER,
  time_on_page INTEGER,
  scroll_depth INTEGER,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  timezone TEXT,
  client_timestamp TIMESTAMPTZ,
  server_timestamp TIMESTAMPTZ default NOW(),
  created_at TIMESTAMPTZ default NOW()
);

alter table public.experience_tracks ENABLE row LEVEL SECURITY;

-- user_sessions
create table if not exists public.user_sessions (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT unique not null,
  user_id UUID,
  anonymous_id TEXT,
  started_at TIMESTAMPTZ default NOW(),
  ended_at TIMESTAMPTZ,
  duration INTEGER,
  page_views INTEGER default 0,
  interactions INTEGER default 0,
  entry_url TEXT,
  entry_page_title TEXT,
  exit_url TEXT,
  exit_page_title TEXT,
  user_agent TEXT,
  device_type TEXT,
  browser_name TEXT,
  os_name TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  bounce BOOLEAN default false,
  converted BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.user_sessions ENABLE row LEVEL SECURITY;

-- user_journeys
create table if not exists public.user_journeys (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID,
  anonymous_id TEXT,
  session_id TEXT,
  journey_type TEXT not null check (
    journey_type in (
      'product_discovery',
      'purchase_funnel',
      'onboarding',
      'support',
      'content_engagement'
    )
  ),
  journey_step TEXT not null,
  step_order INTEGER not null,
  page_url TEXT,
  action_taken TEXT,
  time_spent INTEGER,
  completed BOOLEAN default false,
  dropped_off BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  properties JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.user_journeys ENABLE row LEVEL SECURITY;

-- performance_metrics
create table if not exists public.performance_metrics (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  page_url TEXT not null,
  lcp DECIMAL(8, 2),
  fid DECIMAL(8, 2),
  cls DECIMAL(6, 4),
  fcp DECIMAL(8, 2),
  ttfb DECIMAL(8, 2),
  dns_lookup_time INTEGER,
  tcp_connect_time INTEGER,
  tls_setup_time INTEGER,
  request_time INTEGER,
  response_time INTEGER,
  dom_processing_time INTEGER,
  load_event_time INTEGER,
  custom_metrics JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.performance_metrics ENABLE row LEVEL SECURITY;

-- addresses
create table if not exists public.addresses (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID not null references auth.users (id) on delete CASCADE,
  type TEXT not null check (type in ('shipping', 'billing')),
  first_name TEXT not null,
  last_name TEXT not null,
  address TEXT not null,
  city TEXT not null,
  postal_code TEXT not null,
  country TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.addresses ENABLE row LEVEL SECURITY;

-- reviews - Updated to reference external API product IDs
create table if not exists public.reviews (
  id UUID primary key default uuid_generate_v4 (),
  product_id integer not null, -- Changed from UUID to INTEGER for external API
  user_id UUID not null references auth.users (id) on delete CASCADE,
  rating INTEGER not null check (
    rating >= 1
    and rating <= 5
  ),
  comment TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  unique (product_id, user_id)
);

alter table public.reviews ENABLE row LEVEL SECURITY;

-- newsletter_subscriptions
create table if not exists public.newsletter_subscriptions (
  id UUID primary key default uuid_generate_v4 (),
  email TEXT not null unique,
  subscribed_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW() -- Added missing timestamp
);

alter table public.newsletter_subscriptions ENABLE row LEVEL SECURITY;

-- order_status_history (NEW TABLE)
create table if not exists public.order_status_history (
  id UUID primary key default uuid_generate_v4 (),
  order_id UUID not null references public.orders (id) on delete CASCADE,
  old_status TEXT,
  new_status TEXT not null,
  changed_by UUID references auth.users (id),
  notes TEXT,
  created_at TIMESTAMPTZ default NOW()
);

-- =================================================================
-- Indexes
-- =================================================================
create unique INDEX IF not exists anonymous_cart_items_pkey on public.anonymous_cart_items using btree (id);

create unique INDEX IF not exists anonymous_carts_pkey on public.anonymous_carts using btree (id);

create unique INDEX IF not exists anonymous_carts_session_id_key on public.anonymous_carts using btree (session_id);

create unique INDEX IF not exists cart_items_pkey on public.cart_items using btree (id);

create unique INDEX IF not exists carts_pkey on public.carts using btree (id);

create unique INDEX IF not exists carts_user_id_key on public.carts (user_id);

-- Added unique constraint
create index IF not exists idx_anonymous_cart_items_cart_id on public.anonymous_cart_items using btree (cart_id);

create index IF not exists idx_anonymous_cart_items_product_id on public.anonymous_cart_items using btree (product_id);

create index IF not exists idx_anonymous_cart_items_variant_id on public.anonymous_cart_items using btree (variant_id)
where
  (variant_id is not null);

create index IF not exists idx_anonymous_carts_email on public.anonymous_carts using btree (email)
where
  (email is not null);

create index IF not exists idx_anonymous_carts_expires_at on public.anonymous_carts using btree (expires_at);

create index IF not exists idx_anonymous_carts_session_id on public.anonymous_carts using btree (session_id);

create index IF not exists idx_anonymous_carts_status on public.anonymous_carts using btree (status);

create index IF not exists idx_anonymous_carts_utm_source on public.anonymous_carts using btree (utm_source)
where
  (utm_source is not null);

create unique INDEX IF not exists order_items_pkey on public.order_items using btree (id);

create unique INDEX IF not exists orders_pkey on public.orders using btree (id);

create unique INDEX IF not exists profiles_pkey on public.profiles using btree (id);

-- Composite indexes for performance
create index IF not exists idx_anonymous_carts_status_created_at on public.anonymous_carts (status, created_at);

create index IF not exists idx_orders_user_status on public.orders (user_id, status)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_session_event on public.experience_tracks (session_id, event_type, created_at);

-- GIN indexes for JSONB columns
create index IF not exists idx_anonymous_carts_cart_data_gin on public.anonymous_carts using GIN (cart_data);

create index IF not exists idx_experience_tracks_properties_gin on public.experience_tracks using GIN (custom_properties);

-- Missing foreign key indexes
create index IF not exists idx_cart_items_cart_id on public.cart_items (cart_id);

create index IF not exists idx_cart_items_product_id on public.cart_items (product_id);

create index IF not exists idx_cart_items_variant_id on public.cart_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_order_items_order_id on public.order_items (order_id);

create index IF not exists idx_order_items_product_id on public.order_items (product_id);

create index IF not exists idx_order_items_variant_id on public.order_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_carts_user_id on public.carts (user_id);

-- Unique constraint for cart items
create unique INDEX IF not exists cart_items_cart_product_variant_key on public.cart_items (
  cart_id,
  product_id,
  COALESCE(
    variant_id,
    0
  )
);

-- Additional indexes from original
create index IF not exists idx_experience_tracks_session_id on public.experience_tracks (session_id);

create index IF not exists idx_experience_tracks_user_id on public.experience_tracks (user_id)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_anonymous_id on public.experience_tracks (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_experience_tracks_event_type on public.experience_tracks (event_type);

create index IF not exists idx_experience_tracks_page_url on public.experience_tracks (page_url);

create index IF not exists idx_experience_tracks_created_at on public.experience_tracks (created_at);

create index IF not exists idx_user_sessions_session_id on public.user_sessions (session_id);

create index IF not exists idx_user_sessions_user_id on public.user_sessions (user_id)
where
  user_id is not null;

create index IF not exists idx_user_sessions_started_at on public.user_sessions (started_at);

create index IF not exists idx_user_journeys_user_id on public.user_journeys (user_id)
where
  user_id is not null;

create index IF not exists idx_user_journeys_anonymous_id on public.user_journeys (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_user_journeys_journey_type on public.user_journeys (journey_type);

create index IF not exists idx_user_journeys_session_id on public.user_journeys (session_id);

create index IF not exists idx_performance_metrics_session_id on public.performance_metrics (session_id);

create index IF not exists idx_performance_metrics_page_url on public.performance_metrics (page_url);

create index IF not exists idx_performance_metrics_created_at on public.performance_metrics (created_at);

create index IF not exists idx_anonymous_carts_updated_at on public.anonymous_carts (updated_at);

create index IF not exists idx_orders_anonymous_cart_id on public.orders (anonymous_cart_id)
where
  anonymous_cart_id is not null;

create index IF not exists idx_orders_status on public.orders (status);

create index IF not exists idx_orders_created_at on public.orders (created_at);

create index IF not exists idx_orders_user_id on public.orders (user_id)
where
  user_id is not null;

create index IF not exists idx_addresses_user_id on public.addresses (user_id);

create index IF not exists idx_reviews_product_id on public.reviews (product_id);

create index IF not exists idx_reviews_user_id on public.reviews (user_id);

create index IF not exists idx_order_status_history_order_id on public.order_status_history (order_id);

-- =================================================================
-- Primary Keys & Foreign Keys & Constraints
-- =================================================================
-- Primary Keys
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_pkey" primary key using INDEX "anonymous_cart_items_pkey";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_pkey" primary key using INDEX "anonymous_carts_pkey";

alter table "public"."cart_items"
add constraint "cart_items_pkey" primary key using INDEX "cart_items_pkey";

alter table "public"."carts"
add constraint "carts_pkey" primary key using INDEX "carts_pkey";

alter table "public"."order_items"
add constraint "order_items_pkey" primary key using INDEX "order_items_pkey";

alter table "public"."orders"
add constraint "orders_pkey" primary key using INDEX "orders_pkey";

alter table "public"."profiles"
add constraint "profiles_pkey" primary key using INDEX "profiles_pkey";

-- Foreign Keys & Constraints
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_cart_id_fkey" foreign KEY (cart_id) references anonymous_carts (id) on delete CASCADE;

alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_quantity_check" check ((quantity > 0));

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_session_id_key" unique using INDEX "anonymous_carts_session_id_key";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_status_check" check (
  (
    (
      status = any (
        array[
          'active'::text,
          'abandoned'::text,
          'converted'::text,
          'expired'::text
        ]
      )
    )
  )
);

alter table "public"."cart_items"
add constraint "cart_items_cart_id_fkey" foreign KEY (cart_id) references carts (id) on delete CASCADE;

alter table "public"."carts"
add constraint "carts_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."order_items"
add constraint "order_items_order_id_fkey" foreign KEY (order_id) references orders (id) on delete CASCADE;

alter table "public"."orders"
alter column user_id
drop not null;

alter table "public"."orders"
add constraint "orders_anonymous_cart_id_fkey" foreign KEY (anonymous_cart_id) references public.anonymous_carts (id) on delete set null deferrable initially DEFERRED;

alter table "public"."orders"
add constraint "orders_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."orders"
add constraint orders_user_or_anonymous_check check (
  (
    (user_id is not null)
    or (anonymous_cart_id is not null)
  )
);

alter table "public"."profiles"
add constraint "profiles_id_fkey" foreign KEY (id) references auth.users (id) on delete CASCADE;

-- Check constraints for data integrity
alter table public.order_items
add constraint order_items_price_positive check (price >= 0),
add constraint order_items_quantity_positive check (quantity > 0);

-- Email validation constraints
alter table public.anonymous_carts
add constraint anonymous_carts_email_valid check (
  email is null
  or email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

alter table public.newsletter_subscriptions
add constraint newsletter_subscriptions_email_valid check (
  email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

-- =================================================================
-- Functions
-- =================================================================
create or replace function public.update_updated_at_column () RETURNS trigger LANGUAGE plpgsql as $function$ BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 $function$;

create or replace function public.get_cart_analytics (
  p_start_date timestamp with time zone,
  p_end_date timestamp with time zone
) RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            DATE(created_at) AS date,
            COUNT(*) FILTER (WHERE status = 'active') AS active_carts,
            COUNT(*) FILTER (WHERE status = 'abandoned') AS abandoned_carts,
            COUNT(*) FILTER (WHERE status = 'converted') AS converted_carts,
            AVG(total_value) FILTER (WHERE status = 'converted') AS avg_cart_value,
            AVG(item_count) FILTER (WHERE status = 'converted') AS avg_items_per_cart
        FROM public.anonymous_carts
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(created_at)
    )
    SELECT 
        ds.date,
        COALESCE(ds.active_carts, 0)::INTEGER,
        COALESCE(ds.abandoned_carts, 0)::INTEGER,
        COALESCE(ds.converted_carts, 0)::INTEGER,
        COALESCE(ds.avg_cart_value, 0)::NUMERIC(10,2),
        COALESCE(ds.avg_items_per_cart, 0)::NUMERIC(10,2)
    FROM daily_stats ds
    ORDER BY ds.date;
END;
 $function$;

create or replace function public.get_cart_analytics () RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY SELECT * FROM public.get_cart_analytics(
        (NOW() - INTERVAL '30 days'),
        NOW()
    );
END;
 $function$;

create or replace function public.mark_abandoned_carts (abandonment_minutes INTEGER default 30) RETURNS INTEGER LANGUAGE plpgsql as $function$ DECLARE
    updated_count INTEGER;
BEGIN
    WITH abandoned_carts AS (
        UPDATE public.anonymous_carts
        SET status = 'abandoned',
            updated_at = NOW()
        WHERE status = 'active'
        AND updated_at < (NOW() - (abandonment_minutes * INTERVAL '1 minute'))
        RETURNING 1
    )
    SELECT COUNT(*) INTO updated_count FROM abandoned_carts;
    
    RETURN updated_count;
END;
 $function$;

create or replace function public.update_cart_totals (p_cart_id UUID) RETURNS VOID as $$ BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.trigger_update_cart_totals () RETURNS TRIGGER as $$ BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM public.update_cart_totals(OLD.cart_id);
        RETURN OLD;
    ELSE
        PERFORM public.update_cart_totals(NEW.cart_id);
        RETURN NEW;
    END IF;
END;
 $$ LANGUAGE plpgsql;

create or replace function update_session_stats () RETURNS TRIGGER as $$ BEGIN
    INSERT INTO public.user_sessions (
        session_id, user_id, anonymous_id, started_at, entry_url, entry_page_title,
        user_agent, device_type, browser_name, os_name,
        utm_source, utm_medium, utm_campaign, referrer_url,
        ip_address, country_code, city, page_views, interactions
    )
    VALUES (
        NEW.session_id, NEW.user_id, NEW.anonymous_id, NEW.created_at, NEW.page_url, NEW.page_title,
        NEW.user_agent, NEW.device_type, NEW.browser_name, NEW.os_name,
        NEW.utm_source, NEW.utm_medium, NEW.utm_campaign, NEW.referrer_url,
        NEW.ip_address, NEW.country_code, NEW.city, 
        CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END
    )
    ON CONFLICT (session_id) DO UPDATE SET
        user_id = COALESCE(NEW.user_id, user_sessions.user_id),
        ended_at = NEW.created_at,
        exit_url = NEW.page_url,
        exit_page_title = NEW.page_title,
        page_views = user_sessions.page_views + CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        interactions = user_sessions.interactions + CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END,
        duration = EXTRACT(EPOCH FROM (NEW.created_at - user_sessions.started_at))::INTEGER,
        updated_at = NOW();

    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

create or replace function mark_bounce_sessions () RETURNS INTEGER as $$ DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.user_sessions 
    SET bounce = TRUE, updated_at = NOW()
    WHERE page_views <= 1 
      AND duration < 30 
      AND bounce = FALSE
      AND ended_at < (NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function calculate_funnel_conversion (
  p_journey_type TEXT,
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '30 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  step TEXT,
  step_order INTEGER,
  users BIGINT,
  conversion_rate DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH funnel_steps AS (
        SELECT 
            journey_step,
            step_order,
            COUNT(DISTINCT COALESCE(user_id::TEXT, anonymous_id)) as step_users
        FROM public.user_journeys
        WHERE journey_type = p_journey_type
          AND created_at BETWEEN p_start_date AND p_end_date
        GROUP BY journey_step, step_order
        ORDER BY step_order
    ),
    first_step AS (
        SELECT step_users as first_step_users
        FROM funnel_steps
        ORDER BY step_order
        LIMIT 1
    )
    SELECT 
        fs.journey_step,
        fs.step_order,
        fs.step_users,
        CASE 
            WHEN fst.first_step_users > 0 THEN 
                ROUND((fs.step_users::DECIMAL / fst.first_step_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    CROSS JOIN first_step fst
    ORDER BY fs.step_order;
END;
 $$ LANGUAGE plpgsql;

create or replace function get_user_behavior_insights (
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '7 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  metric_name TEXT,
  metric_value DECIMAL,
  metric_unit TEXT,
  comparison_period_value DECIMAL,
  change_percentage DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN 
            p_start_date - (p_end_date - p_start_date) AND 
            p_start_date
    )
    SELECT 
        'Total Sessions'::TEXT,
        cp.total_sessions::DECIMAL,
        'count'::TEXT,
        pp.total_sessions::DECIMAL,
        CASE WHEN pp.total_sessions > 0 THEN ROUND(((cp.total_sessions - pp.total_sessions)::DECIMAL / pp.total_sessions) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Time on Page'::TEXT,
        ROUND(cp.avg_time_on_page, 2),
        'seconds'::TEXT,
        ROUND(pp.avg_time_on_page, 2),
        CASE WHEN pp.avg_time_on_page > 0 THEN ROUND(((cp.avg_time_on_page - pp.avg_time_on_page) / pp.avg_time_on_page) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Scroll Depth'::TEXT,
        ROUND(cp.avg_scroll_depth, 2),
        'percentage'::TEXT,
        ROUND(pp.avg_scroll_depth, 2),
        CASE WHEN pp.avg_scroll_depth > 0 THEN ROUND(((cp.avg_scroll_depth - pp.avg_scroll_depth) / pp.avg_scroll_depth) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
 $$ LANGUAGE plpgsql;

create or replace function cleanup_old_experience_data () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.experience_tracks WHERE created_at < (NOW() - INTERVAL '90 days');
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM public.user_sessions WHERE created_at < (NOW() - INTERVAL '90 days');
    DELETE FROM public.performance_metrics WHERE created_at < (NOW() - INTERVAL '30 days');
    DELETE FROM public.user_journeys WHERE created_at < (NOW() - INTERVAL '90 days');
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.cleanup_expired_carts () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.anonymous_carts
        WHERE expires_at < NOW()
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.migrate_anonymous_to_user_cart (p_session_id TEXT, p_user_id UUID) RETURNS UUID as $$ DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;
    
    SELECT id INTO v_anonymous_cart_id
    FROM public.anonymous_carts
    WHERE session_id = p_session_id
    AND status = 'active';
    
    IF v_anonymous_cart_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    INSERT INTO public.carts (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id)
    DO UPDATE SET updated_at = NOW()
    RETURNING id INTO v_cart_id;
    
    INSERT INTO public.cart_items (cart_id, product_id, variant_id, quantity)
    SELECT v_cart_id, product_id, variant_id, quantity
    FROM public.anonymous_cart_items
    WHERE cart_id = v_anonymous_cart_id
    ON CONFLICT (cart_id, product_id, variant_id) 
    DO UPDATE SET 
        quantity = cart_items.quantity + EXCLUDED.quantity,
        updated_at = NOW();
    
    UPDATE public.anonymous_carts
    SET status = 'converted',
        updated_at = NOW()
    WHERE id = v_anonymous_cart_id;
    
    RETURN v_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.get_cart_by_session (p_session_id TEXT) RETURNS table (
  cart_id UUID,
  session_id TEXT,
  status TEXT,
  item_count INTEGER,
  total_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) as $$ BEGIN
    RETURN QUERY
    SELECT 
        ac.id AS cart_id,
        ac.session_id,
        ac.status,
        COALESCE(SUM(aci.quantity), 0)::INTEGER AS item_count,
        COALESCE(SUM(aci.price * aci.quantity), 0)::DECIMAL(10,2) AS total_value,
        ac.created_at,
        ac.updated_at
    FROM public.anonymous_carts ac
    LEFT JOIN public.anonymous_cart_items aci ON ac.id = aci.cart_id
    WHERE ac.session_id = p_session_id
    GROUP BY ac.id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.schedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN PERFORM cron.schedule('mark-abandoned-carts', '0 * * * *', 'SELECT public.mark_abandoned_carts(30)'); PERFORM cron.schedule('cleanup-expired-carts', '0 3 * * *', 'SELECT public.cleanup_expired_carts()'); END; $$ LANGUAGE plpgsql;

create or replace function public.unschedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN
    PERFORM cron.unschedule('mark-abandoned-carts');
    PERFORM cron.unschedule('cleanup-expired-carts');
END;
 $$ LANGUAGE plpgsql;

create or replace function public.recover_abandoned_cart (p_session_id TEXT) RETURNS BOOLEAN as $$ DECLARE
    v_updated_rows INTEGER;
BEGIN
    UPDATE public.anonymous_carts
    SET status = 'active',
        updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'abandoned';
    
    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
    RETURN v_updated_rows > 0;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.create_anonymous_order (
  p_anonymous_cart_id UUID,
  p_shipping_address JSONB,
  p_billing_address JSONB,
  p_payment_method TEXT,
  p_status TEXT default 'pending'
) RETURNS UUID as $$ DECLARE
    v_order_id UUID;
    v_cart_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_anonymous_cart_id IS NULL OR p_shipping_address IS NULL OR p_payment_method IS NULL THEN
        RAISE EXCEPTION 'Cart ID, shipping address, and payment method are required';
    END IF;
    
    SELECT EXISTS (
        SELECT 1
        FROM public.anonymous_carts
        WHERE id = p_anonymous_cart_id AND status = 'active'
    ) INTO v_cart_exists;

    IF NOT v_cart_exists THEN
        RAISE EXCEPTION 'Invalid or inactive anonymous cart';
    END IF;

    INSERT INTO public.orders (anonymous_cart_id, status, shipping_address, billing_address, payment_method, created_at, updated_at, total)
    VALUES (p_anonymous_cart_id, p_status, p_shipping_address, p_billing_address, p_payment_method, NOW(), NOW(), (SELECT total_value FROM public.anonymous_carts WHERE id = p_anonymous_cart_id))
    RETURNING id INTO v_order_id;

    UPDATE public.anonymous_carts
    SET status = 'converted', updated_at = NOW()
    WHERE id = p_anonymous_cart_id;

    RETURN v_order_id;
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

create or replace function public.get_order_with_cart (p_order_id UUID) RETURNS JSONB as $$ DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'order_id', o.id,
        'status', o.status,
        'created_at', o.created_at,
        'updated_at', o.updated_at,
        'shipping_address', o.shipping_address,
        'billing_address', o.billing_address,
        'payment_method', o.payment_method,
        'is_guest_order', o.user_id IS NULL,
        'cart', CASE
            WHEN o.anonymous_cart_id IS NOT NULL THEN (
                SELECT jsonb_build_object(
                    'cart_id', ac.id,
                    'session_id', ac.session_id,
                    'created_at', ac.created_at,
                    'items', COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'product_id', aci.product_id,
                            'variant_id', aci.variant_id,
                            'product_title', aci.product_title,
                            'product_image', aci.product_image,
                            'price', aci.price,
                            'quantity', aci.quantity
                        ))
                        FROM public.anonymous_cart_items aci
                        WHERE aci.cart_id = ac.id
                    ), '[]'::jsonb)
                )
                FROM public.anonymous_carts ac
                WHERE ac.id = o.anonymous_cart_id
            )
            ELSE NULL
        END,
        'user', CASE
            WHEN o.user_id IS NOT NULL THEN (
                SELECT jsonb_build_object('id', u.id, 'email', u.email)
                FROM auth.users u
                WHERE u.id = o.user_id
            )
            ELSE NULL
        END
    ) INTO v_result
    FROM public.orders o
    WHERE o.id = p_order_id;
    RETURN v_result;
END;
 $$ LANGUAGE plpgsql STABLE;

create or replace function public.sync_order_cart_status () RETURNS TRIGGER as $$ BEGIN
    IF NEW.status = 'converted' AND OLD.status != 'converted' THEN
        UPDATE public.orders
        SET status = 'processing', updated_at = NOW()
        WHERE anonymous_cart_id = NEW.id AND status = 'pending';
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

-- Rate limiting function
create or replace function check_rate_limit (p_ip_address INET) RETURNS BOOLEAN as $$ DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

-- =================================================================
-- Triggers
-- =================================================================
drop trigger IF exists trigger_update_anonymous_cart_items_updated_at on public.anonymous_cart_items;

create trigger trigger_update_anonymous_cart_items_updated_at BEFORE
update on public.anonymous_cart_items for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_cart_totals_on_delete on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_delete
after DELETE on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_insert on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_insert
after INSERT on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_update on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_update
after
update on public.anonymous_cart_items for EACH row when (
  OLD.quantity is distinct from NEW.quantity
  or OLD.price is distinct from NEW.price
)
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_anonymous_carts_updated_at on public.anonymous_carts;

create trigger trigger_update_anonymous_carts_updated_at BEFORE
update on public.anonymous_carts for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_session_stats on public.experience_tracks;

create trigger trigger_update_session_stats
after INSERT on public.experience_tracks for EACH row
execute FUNCTION update_session_stats ();

drop trigger IF exists trg_sync_order_cart_status on public.anonymous_carts;

create trigger trg_sync_order_cart_status
after
update OF status on public.anonymous_carts for EACH row when (OLD.status is distinct from NEW.status)
execute FUNCTION public.sync_order_cart_status ();

-- Trigger for order_items updated_at
drop trigger IF exists trigger_update_order_items_updated_at on public.order_items;

create trigger trigger_update_order_items_updated_at BEFORE
update on public.order_items for EACH row
execute FUNCTION update_updated_at_column ();

-- Trigger for newsletter_subscriptions updated_at
drop trigger IF exists trigger_update_newsletter_subscriptions_updated_at on public.newsletter_subscriptions;

create trigger trigger_update_newsletter_subscriptions_updated_at BEFORE
update on public.newsletter_subscriptions for EACH row
execute FUNCTION update_updated_at_column ();

-- =================================================================
-- RLS Policies
-- =================================================================
-- Policies for anonymous_cart_items
drop policy IF exists "Allow anonymous access to own cart items" on "public"."anonymous_cart_items";

create policy "Allow service role full access to anonymous_cart_items" on "public"."anonymous_cart_items" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow access to cart items by session" on public.anonymous_cart_items for all using (
  cart_id in (
    select
      id
    from
      public.anonymous_carts
    where
      session_id = current_setting('app.current_session_id', true)::TEXT
  )
);

-- Policies for anonymous_carts
create policy "Allow anonymous access to own cart" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'anon'::text));

create policy "Allow service role full access to anonymous_carts" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow public access with session check" on public.anonymous_carts for all using (true);

-- Policies for cart_items
create policy "Cart items are viewable by cart owner." on "public"."cart_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can delete cart items from their cart." on "public"."cart_items" as permissive for DELETE to public using (
  (
    exists (
      select
        1
      from
        carts
      where
        (
          (carts.id = cart_items.cart_id)
          and (carts.user_id = auth.uid ())
        )
    )
  )
);

create policy "Users can insert cart items for their cart." on "public"."cart_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can update cart items for their cart." on "public"."cart_items" as permissive
for update
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for carts
create policy "Users can create their own cart." on "public"."carts" as permissive for INSERT to public
with
  check ((auth.uid () = user_id));

create policy "Users can update their own cart." on "public"."carts" as permissive
for update
  to public using ((auth.uid () = user_id));

create policy "Users can view their own cart." on "public"."carts" as permissive for
select
  to public using ((auth.uid () = user_id));

-- Policies for order_items
create policy "Order items are viewable by order owner." on "public"."order_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can insert order items for their orders." on "public"."order_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for orders
create policy "Users can create orders" on public.orders for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can view their own orders" on public.orders for
select
  using (auth.uid () = user_id);

create policy "Allow anonymous order creation" on public.orders for INSERT
with
  check (
    (
      anonymous_cart_id is not null
      and user_id is null
    )
  );

drop policy IF exists "Users can update their own orders" on public.orders;

create policy "Users can update their own orders" on public.orders
for update
  using (auth.uid () = user_id)
with
  check (auth.uid () = user_id);

-- Policies for profiles
create policy "Public profiles are viewable by everyone." on "public"."profiles" as permissive for
select
  to public using (true);

create policy "Users can insert their own profile." on "public"."profiles" as permissive for INSERT to public
with
  check ((auth.uid () = id));

create policy "Users can update their own profile." on "public"."profiles" as permissive
for update
  to public using ((auth.uid () = id));

-- Policies for experience_tracks
create policy "Allow service role full access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'authenticated');

create policy "Allow anonymous access to experience_tracks" on public.experience_tracks for INSERT using (auth.role () = 'anon');

-- Policies for user_sessions
create policy "Allow service role full access to user_sessions" on public.user_sessions for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_sessions" on public.user_sessions for all using (auth.role () = 'authenticated');

-- Policies for user_journeys
create policy "Allow service role full access to user_journeys" on public.user_journeys for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_journeys" on public.user_journeys for all using (auth.role () = 'authenticated');

-- Policies for performance_metrics
create policy "Allow service role full access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'authenticated');

-- Policies for addresses
create policy "Users can view their own addresses" on public.addresses for
select
  using (auth.uid () = user_id);

create policy "Users can insert their own addresses" on public.addresses for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own addresses" on public.addresses
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own addresses" on public.addresses for DELETE using (auth.uid () = user_id);

-- Policies for reviews
create policy "Reviews are public" on public.reviews for
select
  using (true);

create policy "Users can insert their own reviews" on public.reviews for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own reviews" on public.reviews
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own reviews" on public.reviews for DELETE using (auth.uid () = user_id);

-- Policies for newsletter_subscriptions
create policy "Public can subscribe to newsletter" on public.newsletter_subscriptions for INSERT
with
  check (true);

create policy "Service roles can manage subscriptions" on public.newsletter_subscriptions for all using (auth.role () = 'service_role');

-- Policies for order_status_history
create policy "Order status history is viewable by order owner" on public.order_status_history for
select
  using (
    exists (
      select
        1
      from
        public.orders o
      where
        o.id = order_status_history.order_id
        and o.user_id = auth.uid ()
    )
  );

create policy "Service role can manage order status history" on public.order_status_history for all using (auth.role () = 'service_role');

-- =================================================================
-- Comments
-- =================================================================
COMMENT on table public.anonymous_carts is 'Stores anonymous shopping carts for users who are not logged in';

COMMENT on column public.anonymous_carts.status is 'Status of the cart: active, abandoned, converted, or expired';

COMMENT on column public.anonymous_carts.utm_source is 'UTM source parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_medium is 'UTM medium parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_campaign is 'UTM campaign parameter for tracking marketing campaigns';

COMMENT on FUNCTION public.mark_abandoned_carts (INTEGER) is 'Marks carts as abandoned after a specified period of inactivity (default 30 minutes)';

COMMENT on FUNCTION public.cleanup_expired_carts () is 'Removes expired carts from the database. Replaces cleanup_expired_anonymous_carts.';

COMMENT on FUNCTION public.migrate_anonymous_to_user_cart (TEXT, UUID) is 'Transfers an anonymous cart to a user account when they log in';

COMMENT on FUNCTION public.get_cart_by_session (TEXT) is 'Retrieves cart summary by session ID';

COMMENT on FUNCTION public.update_cart_totals (UUID) is 'Updates the item count and total value for a cart';

COMMENT on table public.experience_tracks is 'Detailed tracking of user interactions and behavior';

COMMENT on table public.user_sessions is 'Session-level aggregated data for user visits';

COMMENT on table public.user_journeys is 'User journey and funnel tracking for conversion analysis';

COMMENT on table public.performance_metrics is 'Core Web Vitals and performance metrics tracking';

COMMENT on FUNCTION update_session_stats () is 'Automatically updates session statistics when experience tracks are added';

COMMENT on FUNCTION mark_bounce_sessions () is 'Identifies and marks bounce sessions based on behavior';

COMMENT on FUNCTION calculate_funnel_conversion (TEXT, TIMESTAMPTZ, TIMESTAMPTZ) is 'Calculates conversion rates for user journey funnels';

COMMENT on FUNCTION get_user_behavior_insights (TIMESTAMPTZ, TIMESTAMPTZ) is 'Provides behavioral insights with period-over-period comparison';

COMMENT on FUNCTION cleanup_old_experience_data () is 'Cleans up old tracking data to manage database size';

COMMENT on column public.orders.anonymous_cart_id is 'Reference to the anonymous cart for guest checkouts';

COMMENT on constraint orders_user_or_anonymous_check on public.orders is 'Ensures that either user_id or anonymous_cart_id is provided';

COMMENT on FUNCTION public.create_anonymous_order is 'Creates an order from an anonymous cart for guest checkouts';

COMMENT on FUNCTION public.get_order_with_cart is 'Retrieves order details with associated cart information';

COMMENT on table public.addresses is 'Stores shipping and billing addresses for users.';

COMMENT on table public.reviews is 'Stores customer reviews for products.';

COMMENT on table public.newsletter_subscriptions is 'Stores email addresses for newsletter subscribers.';

COMMENT on table public.order_status_history is 'Tracks changes to order status over time.';
```

### User:
ERROR:  42830: there is no unique constraint matching given keys for referenced table "orders"

### Assistant:
I see the issue now. The error is occurring because we're trying to create a foreign key reference to the `orders` table without a unique constraint. Let me fix this by adding the necessary unique constraints and correcting the foreign key relationships.

```sql
-- Combined Schema for Supabase Project: originz
-- Generated from migration files
-- Updated with critical fixes and optimizations
-- =================================================================
-- Extensions
-- =================================================================
create extension IF not exists "uuid-ossp";

create extension IF not exists "pg_cron";

-- =================================================================
-- Tables
-- =================================================================
-- anon cart items
create table if not exists "public"."anonymous_cart_items" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "cart_id" uuid,
  "product_id" integer not null, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "product_title" text,
  "product_image" text,
  "price" numeric(10, 2) not null,
  "quantity" integer not null,
  "added_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_cart_items" ENABLE row LEVEL SECURITY;

-- anon carts
create table if not exists "public"."anonymous_carts" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "session_id" text not null,
  "expires_at" timestamp with time zone not null default (now() + '7 days'::interval),
  "email" text,
  "phone" text,
  "cart_data" jsonb default '{}'::jsonb,
  "total_value" numeric(10, 2) default 0,
  "item_count" integer default 0,
  "utm_source" text,
  "utm_medium" text,
  "utm_campaign" text,
  "referrer" text,
  "user_agent" text,
  "ip_address" text,
  "status" text default 'active'::text,
  "created_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_carts" ENABLE row LEVEL SECURITY;

-- cart items
create table if not exists "public"."cart_items" (
  "id" uuid not null default gen_random_uuid (),
  "cart_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."cart_items" ENABLE row LEVEL SECURITY;

-- carts
create table if not exists "public"."carts" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."carts" ENABLE row LEVEL SECURITY;

-- order items
create table if not exists "public"."order_items" (
  "id" uuid not null default gen_random_uuid (),
  "order_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "price" numeric(10, 2) not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now() -- Added missing timestamp
);

alter table "public"."order_items" ENABLE row LEVEL SECURITY;

-- orders
create table if not exists "public"."orders" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "status" text not null default 'Pending'::text,
  "total" numeric(10, 2) not null,
  "shipping_address" jsonb,
  "billing_address" jsonb,
  "anonymous_cart_id" UUID,
  "payment_method" TEXT -- Added missing column
);

alter table "public"."orders" ENABLE row LEVEL SECURITY;

-- profiles
create table if not exists "public"."profiles" (
  "id" uuid not null,
  "full_name" text,
  "avatar_url" text,
  "billing_address" jsonb,
  "shipping_address" jsonb,
  "updated_at" timestamp with time zone default now()
);

alter table "public"."profiles" ENABLE row LEVEL SECURITY;

-- experience_tracks
create table if not exists public.experience_tracks (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  user_id UUID,
  anonymous_id TEXT,
  event_type TEXT not null check (
    event_type in (
      'page_view',
      'click',
      'scroll',
      'form_interaction',
      'product_view',
      'add_to_cart',
      'search',
      'filter',
      'sort',
      'hover',
      'video_interaction',
      'image_interaction',
      'checkout_step',
      'error',
      'performance'
    )
  ),
  event_name TEXT not null,
  page_url TEXT not null,
  page_title TEXT,
  element_selector TEXT,
  element_text TEXT,
  element_position JSONB,
  interaction_data JSONB default '{}',
  custom_properties JSONB default '{}',
  user_agent TEXT,
  viewport_width INTEGER,
  viewport_height INTEGER,
  screen_width INTEGER,
  screen_height INTEGER,
  device_type TEXT,
  browser_name TEXT,
  browser_version TEXT,
  os_name TEXT,
  os_version TEXT,
  page_load_time INTEGER,
  time_on_page INTEGER,
  scroll_depth INTEGER,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  timezone TEXT,
  client_timestamp TIMESTAMPTZ,
  server_timestamp TIMESTAMPTZ default NOW(),
  created_at TIMESTAMPTZ default NOW()
);

alter table public.experience_tracks ENABLE row LEVEL SECURITY;

-- user_sessions
create table if not exists public.user_sessions (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT unique not null,
  user_id UUID,
  anonymous_id TEXT,
  started_at TIMESTAMPTZ default NOW(),
  ended_at TIMESTAMPTZ,
  duration INTEGER,
  page_views INTEGER default 0,
  interactions INTEGER default 0,
  entry_url TEXT,
  entry_page_title TEXT,
  exit_url TEXT,
  exit_page_title TEXT,
  user_agent TEXT,
  device_type TEXT,
  browser_name TEXT,
  os_name TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  bounce BOOLEAN default false,
  converted BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.user_sessions ENABLE row LEVEL SECURITY;

-- user_journeys
create table if not exists public.user_journeys (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID,
  anonymous_id TEXT,
  session_id TEXT,
  journey_type TEXT not null check (
    journey_type in (
      'product_discovery',
      'purchase_funnel',
      'onboarding',
      'support',
      'content_engagement'
    )
  ),
  journey_step TEXT not null,
  step_order INTEGER not null,
  page_url TEXT,
  action_taken TEXT,
  time_spent INTEGER,
  completed BOOLEAN default false,
  dropped_off BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  properties JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.user_journeys ENABLE row LEVEL SECURITY;

-- performance_metrics
create table if not exists public.performance_metrics (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  page_url TEXT not null,
  lcp DECIMAL(8, 2),
  fid DECIMAL(8, 2),
  cls DECIMAL(6, 4),
  fcp DECIMAL(8, 2),
  ttfb DECIMAL(8, 2),
  dns_lookup_time INTEGER,
  tcp_connect_time INTEGER,
  tls_setup_time INTEGER,
  request_time INTEGER,
  response_time INTEGER,
  dom_processing_time INTEGER,
  load_event_time INTEGER,
  custom_metrics JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.performance_metrics ENABLE row LEVEL SECURITY;

-- addresses
create table if not exists public.addresses (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID not null references auth.users (id) on delete CASCADE,
  type TEXT not null check (type in ('shipping', 'billing')),
  first_name TEXT not null,
  last_name TEXT not null,
  address TEXT not null,
  city TEXT not null,
  postal_code TEXT not null,
  country TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.addresses ENABLE row LEVEL SECURITY;

-- reviews - Updated to reference external API product IDs
create table if not exists public.reviews (
  id UUID primary key default uuid_generate_v4 (),
  product_id integer not null, -- Changed from UUID to INTEGER for external API
  user_id UUID not null references auth.users (id) on delete CASCADE,
  rating INTEGER not null check (
    rating >= 1
    and rating <= 5
  ),
  comment TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  unique (product_id, user_id)
);

alter table public.reviews ENABLE row LEVEL SECURITY;

-- newsletter_subscriptions
create table if not exists public.newsletter_subscriptions (
  id UUID primary key default uuid_generate_v4 (),
  email TEXT not null unique,
  subscribed_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW() -- Added missing timestamp
);

alter table public.newsletter_subscriptions ENABLE row LEVEL SECURITY;

-- order_status_history (NEW TABLE)
create table if not exists public.order_status_history (
  id UUID primary key default uuid_generate_v4 (),
  order_id UUID not null,
  old_status TEXT,
  new_status TEXT not null,
  changed_by UUID references auth.users (id),
  notes TEXT,
  created_at TIMESTAMPTZ default NOW()
);

-- =================================================================
-- Indexes
-- =================================================================
create unique INDEX IF not exists anonymous_cart_items_pkey on public.anonymous_cart_items using btree (id);

create unique INDEX IF not exists anonymous_carts_pkey on public.anonymous_carts using btree (id);

create unique INDEX IF not exists anonymous_carts_session_id_key on public.anonymous_carts using btree (session_id);

create unique INDEX IF not exists cart_items_pkey on public.cart_items using btree (id);

create unique INDEX IF not exists carts_pkey on public.carts using btree (id);

create unique INDEX IF not exists carts_user_id_key on public.carts (user_id);

-- Added unique constraint
create index IF not exists idx_anonymous_cart_items_cart_id on public.anonymous_cart_items using btree (cart_id);

create index IF not exists idx_anonymous_cart_items_product_id on public.anonymous_cart_items using btree (product_id);

create index IF not exists idx_anonymous_cart_items_variant_id on public.anonymous_cart_items using btree (variant_id)
where
  (variant_id is not null);

create index IF not exists idx_anonymous_carts_email on public.anonymous_carts using btree (email)
where
  (email is not null);

create index IF not exists idx_anonymous_carts_expires_at on public.anonymous_carts using btree (expires_at);

create index IF not exists idx_anonymous_carts_session_id on public.anonymous_carts using btree (session_id);

create index IF not exists idx_anonymous_carts_status on public.anonymous_carts using btree (status);

create index IF not exists idx_anonymous_carts_utm_source on public.anonymous_carts using btree (utm_source)
where
  (utm_source is not null);

create unique INDEX IF not exists order_items_pkey on public.order_items using btree (id);

create unique INDEX IF not exists orders_pkey on public.orders using btree (id);

create unique INDEX IF not exists profiles_pkey on public.profiles using btree (id);

-- Composite indexes for performance
create index IF not exists idx_anonymous_carts_status_created_at on public.anonymous_carts (status, created_at);

create index IF not exists idx_orders_user_status on public.orders (user_id, status)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_session_event on public.experience_tracks (session_id, event_type, created_at);

-- GIN indexes for JSONB columns
create index IF not exists idx_anonymous_carts_cart_data_gin on public.anonymous_carts using GIN (cart_data);

create index IF not exists idx_experience_tracks_properties_gin on public.experience_tracks using GIN (custom_properties);

-- Missing foreign key indexes
create index IF not exists idx_cart_items_cart_id on public.cart_items (cart_id);

create index IF not exists idx_cart_items_product_id on public.cart_items (product_id);

create index IF not exists idx_cart_items_variant_id on public.cart_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_order_items_order_id on public.order_items (order_id);

create index IF not exists idx_order_items_product_id on public.order_items (product_id);

create index IF not exists idx_order_items_variant_id on public.order_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_carts_user_id on public.carts (user_id);

-- Unique constraint for cart items
create unique INDEX IF not exists cart_items_cart_product_variant_key on public.cart_items (
  cart_id,
  product_id,
  COALESCE(
    variant_id,
    0
  )
);

-- Additional indexes from original
create index IF not exists idx_experience_tracks_session_id on public.experience_tracks (session_id);

create index IF not exists idx_experience_tracks_user_id on public.experience_tracks (user_id)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_anonymous_id on public.experience_tracks (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_experience_tracks_event_type on public.experience_tracks (event_type);

create index IF not exists idx_experience_tracks_page_url on public.experience_tracks (page_url);

create index IF not exists idx_experience_tracks_created_at on public.experience_tracks (created_at);

create index IF not exists idx_user_sessions_session_id on public.user_sessions (session_id);

create index IF not exists idx_user_sessions_user_id on public.user_sessions (user_id)
where
  user_id is not null;

create index IF not exists idx_user_sessions_started_at on public.user_sessions (started_at);

create index IF not exists idx_user_journeys_user_id on public.user_journeys (user_id)
where
  user_id is not null;

create index IF not exists idx_user_journeys_anonymous_id on public.user_journeys (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_user_journeys_journey_type on public.user_journeys (journey_type);

create index IF not exists idx_user_journeys_session_id on public.user_journeys (session_id);

create index IF not exists idx_performance_metrics_session_id on public.performance_metrics (session_id);

create index IF not exists idx_performance_metrics_page_url on public.performance_metrics (page_url);

create index IF not exists idx_performance_metrics_created_at on public.performance_metrics (created_at);

create index IF not exists idx_anonymous_carts_updated_at on public.anonymous_carts (updated_at);

create index IF not exists idx_orders_anonymous_cart_id on public.orders (anonymous_cart_id)
where
  anonymous_cart_id is not null;

create index IF not exists idx_orders_status on public.orders (status);

create index IF not exists idx_orders_created_at on public.orders (created_at);

create index IF not exists idx_orders_user_id on public.orders (user_id)
where
  user_id is not null;

create index IF not exists idx_addresses_user_id on public.addresses (user_id);

create index IF not exists idx_reviews_product_id on public.reviews (product_id);

create index IF not exists idx_reviews_user_id on public.reviews (user_id);

create index IF not exists idx_order_status_history_order_id on public.order_status_history (order_id);

-- =================================================================
-- Primary Keys & Foreign Keys & Constraints
-- =================================================================
-- Primary Keys
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_pkey" primary key using INDEX "anonymous_cart_items_pkey";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_pkey" primary key using INDEX "anonymous_carts_pkey";

alter table "public"."cart_items"
add constraint "cart_items_pkey" primary key using INDEX "cart_items_pkey";

alter table "public"."carts"
add constraint "carts_pkey" primary key using INDEX "carts_pkey";

alter table "public"."order_items"
add constraint "order_items_pkey" primary key using INDEX "order_items_pkey";

alter table "public"."orders"
add constraint "orders_pkey" primary key using INDEX "orders_pkey";

alter table "public"."profiles"
add constraint "profiles_pkey" primary key using INDEX "profiles_pkey";

-- Foreign Keys & Constraints
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_cart_id_fkey" foreign KEY (cart_id) references anonymous_carts (id) on delete CASCADE;

alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_quantity_check" check ((quantity > 0));

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_session_id_key" unique using INDEX "anonymous_carts_session_id_key";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_status_check" check (
  (
    (
      status = any (
        array[
          'active'::text,
          'abandoned'::text,
          'converted'::text,
          'expired'::text
        ]
      )
    )
  )
);

alter table "public"."cart_items"
add constraint "cart_items_cart_id_fkey" foreign KEY (cart_id) references carts (id) on delete CASCADE;

alter table "public"."carts"
add constraint "carts_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."order_items"
add constraint "order_items_order_id_fkey" foreign KEY (order_id) references orders (id) on delete CASCADE;

alter table "public"."orders"
alter column user_id
drop not null;

alter table "public"."orders"
add constraint "orders_anonymous_cart_id_fkey" foreign KEY (anonymous_cart_id) references public.anonymous_carts (id) on delete set null deferrable initially DEFERRED;

alter table "public"."orders"
add constraint "orders_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."orders"
add constraint orders_user_or_anonymous_check check (
  (
    (user_id is not null)
    or (anonymous_cart_id is not null)
  )
);

alter table "public"."profiles"
add constraint "profiles_id_fkey" foreign KEY (id) references auth.users (id) on delete CASCADE;

-- Check constraints for data integrity
alter table public.order_items
add constraint order_items_price_positive check (price >= 0),
add constraint order_items_quantity_positive check (quantity > 0);

-- Email validation constraints
alter table public.anonymous_carts
add constraint anonymous_carts_email_valid check (
  email is null
  or email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

alter table public.newsletter_subscriptions
add constraint newsletter_subscriptions_email_valid check (
  email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

-- =================================================================
-- Functions
-- =================================================================
create or replace function public.update_updated_at_column () RETURNS trigger LANGUAGE plpgsql as $function$ BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 $function$;

create or replace function public.get_cart_analytics (
  p_start_date timestamp with time zone,
  p_end_date timestamp with time zone
) RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            DATE(created_at) AS date,
            COUNT(*) FILTER (WHERE status = 'active') AS active_carts,
            COUNT(*) FILTER (WHERE status = 'abandoned') AS abandoned_carts,
            COUNT(*) FILTER (WHERE status = 'converted') AS converted_carts,
            AVG(total_value) FILTER (WHERE status = 'converted') AS avg_cart_value,
            AVG(item_count) FILTER (WHERE status = 'converted') AS avg_items_per_cart
        FROM public.anonymous_carts
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(created_at)
    )
    SELECT 
        ds.date,
        COALESCE(ds.active_carts, 0)::INTEGER,
        COALESCE(ds.abandoned_carts, 0)::INTEGER,
        COALESCE(ds.converted_carts, 0)::INTEGER,
        COALESCE(ds.avg_cart_value, 0)::NUMERIC(10,2),
        COALESCE(ds.avg_items_per_cart, 0)::NUMERIC(10,2)
    FROM daily_stats ds
    ORDER BY ds.date;
END;
 $function$;

create or replace function public.get_cart_analytics () RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY SELECT * FROM public.get_cart_analytics(
        (NOW() - INTERVAL '30 days'),
        NOW()
    );
END;
 $function$;

create or replace function public.mark_abandoned_carts (abandonment_minutes INTEGER default 30) RETURNS INTEGER LANGUAGE plpgsql as $function$ DECLARE
    updated_count INTEGER;
BEGIN
    WITH abandoned_carts AS (
        UPDATE public.anonymous_carts
        SET status = 'abandoned',
            updated_at = NOW()
        WHERE status = 'active'
        AND updated_at < (NOW() - (abandonment_minutes * INTERVAL '1 minute'))
        RETURNING 1
    )
    SELECT COUNT(*) INTO updated_count FROM abandoned_carts;
    
    RETURN updated_count;
END;
 $function$;

create or replace function public.update_cart_totals (p_cart_id UUID) RETURNS VOID as $$ BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.trigger_update_cart_totals () RETURNS TRIGGER as $$ BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM public.update_cart_totals(OLD.cart_id);
        RETURN OLD;
    ELSE
        PERFORM public.update_cart_totals(NEW.cart_id);
        RETURN NEW;
    END IF;
END;
 $$ LANGUAGE plpgsql;

create or replace function update_session_stats () RETURNS TRIGGER as $$ BEGIN
    INSERT INTO public.user_sessions (
        session_id, user_id, anonymous_id, started_at, entry_url, entry_page_title,
        user_agent, device_type, browser_name, os_name,
        utm_source, utm_medium, utm_campaign, referrer_url,
        ip_address, country_code, city, page_views, interactions
    )
    VALUES (
        NEW.session_id, NEW.user_id, NEW.anonymous_id, NEW.created_at, NEW.page_url, NEW.page_title,
        NEW.user_agent, NEW.device_type, NEW.browser_name, NEW.os_name,
        NEW.utm_source, NEW.utm_medium, NEW.utm_campaign, NEW.referrer_url,
        NEW.ip_address, NEW.country_code, NEW.city, 
        CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END
    )
    ON CONFLICT (session_id) DO UPDATE SET
        user_id = COALESCE(NEW.user_id, user_sessions.user_id),
        ended_at = NEW.created_at,
        exit_url = NEW.page_url,
        exit_page_title = NEW.page_title,
        page_views = user_sessions.page_views + CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        interactions = user_sessions.interactions + CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END,
        duration = EXTRACT(EPOCH FROM (NEW.created_at - user_sessions.started_at))::INTEGER,
        updated_at = NOW();

    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

create or replace function mark_bounce_sessions () RETURNS INTEGER as $$ DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.user_sessions 
    SET bounce = TRUE, updated_at = NOW()
    WHERE page_views <= 1 
      AND duration < 30 
      AND bounce = FALSE
      AND ended_at < (NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function calculate_funnel_conversion (
  p_journey_type TEXT,
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '30 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  step TEXT,
  step_order INTEGER,
  users BIGINT,
  conversion_rate DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH funnel_steps AS (
        SELECT 
            journey_step,
            step_order,
            COUNT(DISTINCT COALESCE(user_id::TEXT, anonymous_id)) as step_users
        FROM public.user_journeys
        WHERE journey_type = p_journey_type
          AND created_at BETWEEN p_start_date AND p_end_date
        GROUP BY journey_step, step_order
        ORDER BY step_order
    ),
    first_step AS (
        SELECT step_users as first_step_users
        FROM funnel_steps
        ORDER BY step_order
        LIMIT 1
    )
    SELECT 
        fs.journey_step,
        fs.step_order,
        fs.step_users,
        CASE 
            WHEN fst.first_step_users > 0 THEN 
                ROUND((fs.step_users::DECIMAL / fst.first_step_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    CROSS JOIN first_step fst
    ORDER BY fs.step_order;
END;
 $$ LANGUAGE plpgsql;

create or replace function get_user_behavior_insights (
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '7 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  metric_name TEXT,
  metric_value DECIMAL,
  metric_unit TEXT,
  comparison_period_value DECIMAL,
  change_percentage DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN 
            p_start_date - (p_end_date - p_start_date) AND 
            p_start_date
    )
    SELECT 
        'Total Sessions'::TEXT,
        cp.total_sessions::DECIMAL,
        'count'::TEXT,
        pp.total_sessions::DECIMAL,
        CASE WHEN pp.total_sessions > 0 THEN ROUND(((cp.total_sessions - pp.total_sessions)::DECIMAL / pp.total_sessions) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Time on Page'::TEXT,
        ROUND(cp.avg_time_on_page, 2),
        'seconds'::TEXT,
        ROUND(pp.avg_time_on_page, 2),
        CASE WHEN pp.avg_time_on_page > 0 THEN ROUND(((cp.avg_time_on_page - pp.avg_time_on_page) / pp.avg_time_on_page) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Scroll Depth'::TEXT,
        ROUND(cp.avg_scroll_depth, 2),
        'percentage'::TEXT,
        ROUND(pp.avg_scroll_depth, 2),
        CASE WHEN pp.avg_scroll_depth > 0 THEN ROUND(((cp.avg_scroll_depth - pp.avg_scroll_depth) / pp.avg_scroll_depth) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
 $$ LANGUAGE plpgsql;

create or replace function cleanup_old_experience_data () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.experience_tracks WHERE created_at < (NOW() - INTERVAL '90 days');
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM public.user_sessions WHERE created_at < (NOW() - INTERVAL '90 days');
    DELETE FROM public.performance_metrics WHERE created_at < (NOW() - INTERVAL '30 days');
    DELETE FROM public.user_journeys WHERE created_at < (NOW() - INTERVAL '90 days');
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.cleanup_expired_carts () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.anonymous_carts
        WHERE expires_at < NOW()
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.migrate_anonymous_to_user_cart (p_session_id TEXT, p_user_id UUID) RETURNS UUID as $$ DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;
    
    SELECT id INTO v_anonymous_cart_id
    FROM public.anonymous_carts
    WHERE session_id = p_session_id
    AND status = 'active';
    
    IF v_anonymous_cart_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    INSERT INTO public.carts (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id)
    DO UPDATE SET updated_at = NOW()
    RETURNING id INTO v_cart_id;
    
    INSERT INTO public.cart_items (cart_id, product_id, variant_id, quantity)
    SELECT v_cart_id, product_id, variant_id, quantity
    FROM public.anonymous_cart_items
    WHERE cart_id = v_anonymous_cart_id
    ON CONFLICT (cart_id, product_id, variant_id) 
    DO UPDATE SET 
        quantity = cart_items.quantity + EXCLUDED.quantity,
        updated_at = NOW();
    
    UPDATE public.anonymous_carts
    SET status = 'converted',
        updated_at = NOW()
    WHERE id = v_anonymous_cart_id;
    
    RETURN v_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.get_cart_by_session (p_session_id TEXT) RETURNS table (
  cart_id UUID,
  session_id TEXT,
  status TEXT,
  item_count INTEGER,
  total_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) as $$ BEGIN
    RETURN QUERY
    SELECT 
        ac.id AS cart_id,
        ac.session_id,
        ac.status,
        COALESCE(SUM(aci.quantity), 0)::INTEGER AS item_count,
        COALESCE(SUM(aci.price * aci.quantity), 0)::DECIMAL(10,2) AS total_value,
        ac.created_at,
        ac.updated_at
    FROM public.anonymous_carts ac
    LEFT JOIN public.anonymous_cart_items aci ON ac.id = aci.cart_id
    WHERE ac.session_id = p_session_id
    GROUP BY ac.id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.schedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN PERFORM cron.schedule('mark-abandoned-carts', '0 * * * *', 'SELECT public.mark_abandoned_carts(30)'); PERFORM cron.schedule('cleanup-expired-carts', '0 3 * * *', 'SELECT public.cleanup_expired_carts()'); END; $$ LANGUAGE plpgsql;

create or replace function public.unschedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN
    PERFORM cron.unschedule('mark-abandoned-carts');
    PERFORM cron.unschedule('cleanup-expired-carts');
END;
 $$ LANGUAGE plpgsql;

create or replace function public.recover_abandoned_cart (p_session_id TEXT) RETURNS BOOLEAN as $$ DECLARE
    v_updated_rows INTEGER;
BEGIN
    UPDATE public.anonymous_carts
    SET status = 'active',
        updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'abandoned';
    
    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
    RETURN v_updated_rows > 0;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.create_anonymous_order (
  p_anonymous_cart_id UUID,
  p_shipping_address JSONB,
  p_billing_address JSONB,
  p_payment_method TEXT,
  p_status TEXT default 'pending'
) RETURNS UUID as $$ DECLARE
    v_order_id UUID;
    v_cart_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_anonymous_cart_id IS NULL OR p_shipping_address IS NULL OR p_payment_method IS NULL THEN
        RAISE EXCEPTION 'Cart ID, shipping address, and payment method are required';
    END IF;
    
    SELECT EXISTS (
        SELECT 1
        FROM public.anonymous_carts
        WHERE id = p_anonymous_cart_id AND status = 'active'
    ) INTO v_cart_exists;

    IF NOT v_cart_exists THEN
        RAISE EXCEPTION 'Invalid or inactive anonymous cart';
    END IF;

    INSERT INTO public.orders (anonymous_cart_id, status, shipping_address, billing_address, payment_method, created_at, updated_at, total)
    VALUES (p_anonymous_cart_id, p_status, p_shipping_address, p_billing_address, p_payment_method, NOW(), NOW(), (SELECT total_value FROM public.anonymous_carts WHERE id = p_anonymous_cart_id))
    RETURNING id INTO v_order_id;

    UPDATE public.anonymous_carts
    SET status = 'converted', updated_at = NOW()
    WHERE id = p_anonymous_cart_id;

    RETURN v_order_id;
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

create or replace function public.get_order_with_cart (p_order_id UUID) RETURNS JSONB as $$ DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'order_id', o.id,
        'status', o.status,
        'created_at', o.created_at,
        'updated_at', o.updated_at,
        'shipping_address', o.shipping_address,
        'billing_address', o.billing_address,
        'payment_method', o.payment_method,
        'is_guest_order', o.user_id IS NULL,
        'cart', CASE
            WHEN o.anonymous_cart_id IS NOT NULL THEN (
                SELECT jsonb_build_object(
                    'cart_id', ac.id,
                    'session_id', ac.session_id,
                    'created_at', ac.created_at,
                    'items', COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'product_id', aci.product_id,
                            'variant_id', aci.variant_id,
                            'product_title', aci.product_title,
                            'product_image', aci.product_image,
                            'price', aci.price,
                            'quantity', aci.quantity
                        ))
                        FROM public.anonymous_cart_items aci
                        WHERE aci.cart_id = ac.id
                    ), '[]'::jsonb)
                )
                FROM public.anonymous_carts ac
                WHERE ac.id = o.anonymous_cart_id
            )
            ELSE NULL
        END,
        'user', CASE
            WHEN o.user_id IS NOT NULL THEN (
                SELECT jsonb_build_object('id', u.id, 'email', u.email)
                FROM auth.users u
                WHERE u.id = o.user_id
            )
            ELSE NULL
        END
    ) INTO v_result
    FROM public.orders o
    WHERE o.id = p_order_id;
    RETURN v_result;
END;
 $$ LANGUAGE plpgsql STABLE;

create or replace function public.sync_order_cart_status () RETURNS TRIGGER as $$ BEGIN
    IF NEW.status = 'converted' AND OLD.status != 'converted' THEN
        UPDATE public.orders
        SET status = 'processing', updated_at = NOW()
        WHERE anonymous_cart_id = NEW.id AND status = 'pending';
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

-- Rate limiting function
create or replace function check_rate_limit (p_ip_address INET) RETURNS BOOLEAN as $$ DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

-- =================================================================
-- Triggers
-- =================================================================
drop trigger IF exists trigger_update_anonymous_cart_items_updated_at on public.anonymous_cart_items;

create trigger trigger_update_anonymous_cart_items_updated_at BEFORE
update on public.anonymous_cart_items for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_cart_totals_on_delete on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_delete
after DELETE on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_insert on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_insert
after INSERT on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_update on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_update
after
update on public.anonymous_cart_items for EACH row when (
  OLD.quantity is distinct from NEW.quantity
  or OLD.price is distinct from NEW.price
)
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_anonymous_carts_updated_at on public.anonymous_carts;

create trigger trigger_update_anonymous_carts_updated_at BEFORE
update on public.anonymous_carts for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_session_stats on public.experience_tracks;

create trigger trigger_update_session_stats
after INSERT on public.experience_tracks for EACH row
execute FUNCTION update_session_stats ();

drop trigger IF exists trg_sync_order_cart_status on public.anonymous_carts;

create trigger trg_sync_order_cart_status
after
update OF status on public.anonymous_carts for EACH row when (OLD.status is distinct from NEW.status)
execute FUNCTION public.sync_order_cart_status ();

-- Trigger for order_items updated_at
drop trigger IF exists trigger_update_order_items_updated_at on public.order_items;

create trigger trigger_update_order_items_updated_at BEFORE
update on public.order_items for EACH row
execute FUNCTION update_updated_at_column ();

-- Trigger for newsletter_subscriptions updated_at
drop trigger IF exists trigger_update_newsletter_subscriptions_updated_at on public.newsletter_subscriptions;

create trigger trigger_update_newsletter_subscriptions_updated_at BEFORE
update on public.newsletter_subscriptions for EACH row
execute FUNCTION update_updated_at_column ();

-- =================================================================
-- RLS Policies
-- =================================================================
-- Policies for anonymous_cart_items
drop policy IF exists "Allow anonymous access to own cart items" on "public"."anonymous_cart_items";

create policy "Allow service role full access to anonymous_cart_items" on "public"."anonymous_cart_items" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow access to cart items by session" on public.anonymous_cart_items for all using (
  cart_id in (
    select
      id
    from
      public.anonymous_carts
    where
      session_id = current_setting('app.current_session_id', true)::TEXT
  )
);

-- Policies for anonymous_carts
create policy "Allow anonymous access to own cart" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'anon'::text));

create policy "Allow service role full access to anonymous_carts" on "public"."anonymous_carts" as permissive for all to public using ((auth.role () = 'service_role'::text));

create policy "Allow public access with session check" on public.anonymous_carts for all using (true);

-- Policies for cart_items
create policy "Cart items are viewable by cart owner." on "public"."cart_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can delete cart items from their cart." on "public"."cart_items" as permissive for DELETE to public using (
  (
    exists (
      select
        1
      from
        carts
      where
        (
          (carts.id = cart_items.cart_id)
          and (carts.user_id = auth.uid ())
        )
    )
  )
);

create policy "Users can insert cart items for their cart." on "public"."cart_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can update cart items for their cart." on "public"."cart_items" as permissive
for update
  to public using (
    (
      exists (
        select
          1
        from
          carts
        where
          (
            (carts.id = cart_items.cart_id)
            and (carts.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for carts
create policy "Users can create their own cart." on "public"."carts" as permissive for INSERT to public
with
  check ((auth.uid () = user_id));

create policy "Users can update their own cart." on "public"."carts" as permissive
for update
  to public using ((auth.uid () = user_id));

create policy "Users can view their own cart." on "public"."carts" as permissive for
select
  to public using ((auth.uid () = user_id));

-- Policies for order_items
create policy "Order items are viewable by order owner." on "public"."order_items" as permissive for
select
  to public using (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

create policy "Users can insert order items for their orders." on "public"."order_items" as permissive for INSERT to public
with
  check (
    (
      exists (
        select
          1
        from
          orders
        where
          (
            (orders.id = order_items.order_id)
            and (orders.user_id = auth.uid ())
          )
      )
    )
  );

-- Policies for orders
create policy "Users can create orders" on public.orders for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can view their own orders" on public.orders for
select
  using (auth.uid () = user_id);

create policy "Allow anonymous order creation" on public.orders for INSERT
with
  check (
    (
      anonymous_cart_id is not null
      and user_id is null
    )
  );

drop policy IF exists "Users can update their own orders" on public.orders;

create policy "Users can update their own orders" on public.orders
for update
  using (auth.uid () = user_id)
with
  check (auth.uid () = user_id);

-- Policies for profiles
create policy "Public profiles are viewable by everyone." on "public"."profiles" as permissive for
select
  to public using (true);

create policy "Users can insert their own profile." on "public"."profiles" as permissive for INSERT to public
with
  check ((auth.uid () = id));

create policy "Users can update their own profile." on "public"."profiles" as permissive
for update
  to public using ((auth.uid () = id));

-- Policies for experience_tracks
create policy "Allow service role full access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to experience_tracks" on public.experience_tracks for all using (auth.role () = 'authenticated');

create policy "Allow anonymous access to experience_tracks" on public.experience_tracks for INSERT using (auth.role () = 'anon');

-- Policies for user_sessions
create policy "Allow service role full access to user_sessions" on public.user_sessions for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_sessions" on public.user_sessions for all using (auth.role () = 'authenticated');

-- Policies for user_journeys
create policy "Allow service role full access to user_journeys" on public.user_journeys for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to user_journeys" on public.user_journeys for all using (auth.role () = 'authenticated');

-- Policies for performance_metrics
create policy "Allow service role full access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'service_role');

create policy "Allow authenticated access to performance_metrics" on public.performance_metrics for all using (auth.role () = 'authenticated');

-- Policies for addresses
create policy "Users can view their own addresses" on public.addresses for
select
  using (auth.uid () = user_id);

create policy "Users can insert their own addresses" on public.addresses for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own addresses" on public.addresses
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own addresses" on public.addresses for DELETE using (auth.uid () = user_id);

-- Policies for reviews
create policy "Reviews are public" on public.reviews for
select
  using (true);

create policy "Users can insert their own reviews" on public.reviews for INSERT
with
  check (auth.uid () = user_id);

create policy "Users can update their own reviews" on public.reviews
for update
  using (auth.uid () = user_id);

create policy "Users can delete their own reviews" on public.reviews for DELETE using (auth.uid () = user_id);

-- Policies for newsletter_subscriptions
create policy "Public can subscribe to newsletter" on public.newsletter_subscriptions for INSERT
with
  check (true);

create policy "Service roles can manage subscriptions" on public.newsletter_subscriptions for all using (auth.role () = 'service_role');

-- Policies for order_status_history
create policy "Order status history is viewable by order owner" on public.order_status_history for
select
  using (
    exists (
      select
        1
      from
        public.orders o
      where
        o.id = order_status_history.order_id
        and o.user_id = auth.uid ()
    )
  );

create policy "Service role can manage order status history" on public.order_status_history for all using (auth.role () = 'service_role');

-- =================================================================
-- Comments
-- =================================================================
COMMENT on table public.anonymous_carts is 'Stores anonymous shopping carts for users who are not logged in';

COMMENT on column public.anonymous_carts.status is 'Status of the cart: active, abandoned, converted, or expired';

COMMENT on column public.anonymous_carts.utm_source is 'UTM source parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_medium is 'UTM medium parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_campaign is 'UTM campaign parameter for tracking marketing campaigns';

COMMENT on FUNCTION public.mark_abandoned_carts (INTEGER) is 'Marks carts as abandoned after a specified period of inactivity (default 30 minutes)';

COMMENT on FUNCTION public.cleanup_expired_carts () is 'Removes expired carts from the database. Replaces cleanup_expired_anonymous_carts.';

COMMENT on FUNCTION public.migrate_anonymous_to_user_cart (TEXT, UUID) is 'Transfers an anonymous cart to a user account when they log in';

COMMENT on FUNCTION public.get_cart_by_session (TEXT) is 'Retrieves cart summary by session ID';

COMMENT on FUNCTION public.update_cart_totals (UUID) is 'Updates the item count and total value for a cart';

COMMENT on table public.experience_tracks is 'Detailed tracking of user interactions and behavior';

COMMENT on table public.user_sessions is 'Session-level aggregated data for user visits';

COMMENT on table public.user_journeys is 'User journey and funnel tracking for conversion analysis';

COMMENT on table public.performance_metrics is 'Core Web Vitals and performance metrics tracking';

COMMENT on FUNCTION update_session_stats () is 'Automatically updates session statistics when experience tracks are added';

COMMENT on FUNCTION mark_bounce_sessions () is 'Identifies and marks bounce sessions based on behavior';

COMMENT on FUNCTION calculate_funnel_conversion (TEXT, TIMESTAMPTZ, TIMESTAMPTZ) is 'Calculates conversion rates for user journey funnels';

COMMENT on FUNCTION get_user_behavior_insights (TIMESTAMPTZ, TIMESTAMPTZ) is 'Provides behavioral insights with period-over-period comparison';

COMMENT on FUNCTION cleanup_old_experience_data () is 'Cleans up old tracking data to manage database size';

COMMENT on column public.orders.anonymous_cart_id is 'Reference to the anonymous cart for guest checkouts';

COMMENT on constraint orders_user_or_anonymous_check on public.orders is 'Ensures that either user_id or anonymous_cart_id is provided';

COMMENT on FUNCTION public.create_anonymous_order is 'Creates an order from an anonymous cart for guest checkouts';

COMMENT on FUNCTION public.get_order_with_cart is 'Retrieves order details with associated cart information';

COMMENT on table public.addresses is 'Stores shipping and billing addresses for users.';

COMMENT on table public.reviews is 'Stores customer reviews for products.';

COMMENT on table public.newsletter_subscriptions is 'Stores email addresses for newsletter subscribers.';

COMMENT on table public.order_status_history is 'Tracks changes to order status over time.';
```

### User:
ERROR:  42601: only WITH CHECK expression allowed for INSERT

### Assistant:
You're right! The issue is with the RLS policies for INSERT operations. In PostgreSQL, INSERT policies can only use `WITH CHECK` expressions, not `USING`. Let me fix all the policies that have this issue:

```sql
-- Combined Schema for Supabase Project: originz
-- Generated from migration files
-- Updated with critical fixes and optimizations
-- =================================================================
-- Extensions
-- =================================================================
create extension IF not exists "uuid-ossp";

create extension IF not exists "pg_cron";

-- =================================================================
-- Tables
-- =================================================================
-- anon cart items
create table if not exists "public"."anonymous_cart_items" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "cart_id" uuid,
  "product_id" integer not null, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "product_title" text,
  "product_image" text,
  "price" numeric(10, 2) not null,
  "quantity" integer not null,
  "added_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_cart_items" ENABLE row LEVEL SECURITY;

-- anon carts
create table if not exists "public"."anonymous_carts" (
  "id" uuid not null default extensions.uuid_generate_v4 (),
  "session_id" text not null,
  "expires_at" timestamp with time zone not null default (now() + '7 days'::interval),
  "email" text,
  "phone" text,
  "cart_data" jsonb default '{}'::jsonb,
  "total_value" numeric(10, 2) default 0,
  "item_count" integer default 0,
  "utm_source" text,
  "utm_medium" text,
  "utm_campaign" text,
  "referrer" text,
  "user_agent" text,
  "ip_address" text,
  "status" text default 'active'::text,
  "created_at" timestamp with time zone default now(),
  "updated_at" timestamp with time zone default now()
);

alter table "public"."anonymous_carts" ENABLE row LEVEL SECURITY;

-- cart items
create table if not exists "public"."cart_items" (
  "id" uuid not null default gen_random_uuid (),
  "cart_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."cart_items" ENABLE row LEVEL SECURITY;

-- carts
create table if not exists "public"."carts" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now()
);

alter table "public"."carts" ENABLE row LEVEL SECURITY;

-- order items
create table if not exists "public"."order_items" (
  "id" uuid not null default gen_random_uuid (),
  "order_id" uuid,
  "product_id" integer, -- Changed from UUID to INTEGER for external API
  "variant_id" integer, -- Changed from UUID to INTEGER for external API
  "quantity" integer not null,
  "price" numeric(10, 2) not null,
  "created_at" timestamp with time zone not null default now(),
  "updated_at" timestamp with time zone not null default now() -- Added missing timestamp
);

alter table "public"."order_items" ENABLE row LEVEL SECURITY;

-- orders
create table if not exists "public"."orders" (
  "id" uuid not null default gen_random_uuid (),
  "user_id" uuid,
  "created_at" timestamp with time zone not null default now(),
  "status" text not null default 'Pending'::text,
  "total" numeric(10, 2) not null,
  "shipping_address" jsonb,
  "billing_address" jsonb,
  "anonymous_cart_id" UUID,
  "payment_method" TEXT -- Added missing column
);

alter table "public"."orders" ENABLE row LEVEL SECURITY;

-- profiles
create table if not exists "public"."profiles" (
  "id" uuid not null,
  "full_name" text,
  "avatar_url" text,
  "billing_address" jsonb,
  "shipping_address" jsonb,
  "updated_at" timestamp with time zone default now()
);

alter table "public"."profiles" ENABLE row LEVEL SECURITY;

-- experience_tracks
create table if not exists public.experience_tracks (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  user_id UUID,
  anonymous_id TEXT,
  event_type TEXT not null check (
    event_type in (
      'page_view',
      'click',
      'scroll',
      'form_interaction',
      'product_view',
      'add_to_cart',
      'search',
      'filter',
      'sort',
      'hover',
      'video_interaction',
      'image_interaction',
      'checkout_step',
      'error',
      'performance'
    )
  ),
  event_name TEXT not null,
  page_url TEXT not null,
  page_title TEXT,
  element_selector TEXT,
  element_text TEXT,
  element_position JSONB,
  interaction_data JSONB default '{}',
  custom_properties JSONB default '{}',
  user_agent TEXT,
  viewport_width INTEGER,
  viewport_height INTEGER,
  screen_width INTEGER,
  screen_height INTEGER,
  device_type TEXT,
  browser_name TEXT,
  browser_version TEXT,
  os_name TEXT,
  os_version TEXT,
  page_load_time INTEGER,
  time_on_page INTEGER,
  scroll_depth INTEGER,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  timezone TEXT,
  client_timestamp TIMESTAMPTZ,
  server_timestamp TIMESTAMPTZ default NOW(),
  created_at TIMESTAMPTZ default NOW()
);

alter table public.experience_tracks ENABLE row LEVEL SECURITY;

-- user_sessions
create table if not exists public.user_sessions (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT unique not null,
  user_id UUID,
  anonymous_id TEXT,
  started_at TIMESTAMPTZ default NOW(),
  ended_at TIMESTAMPTZ,
  duration INTEGER,
  page_views INTEGER default 0,
  interactions INTEGER default 0,
  entry_url TEXT,
  entry_page_title TEXT,
  exit_url TEXT,
  exit_page_title TEXT,
  user_agent TEXT,
  device_type TEXT,
  browser_name TEXT,
  os_name TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  referrer_url TEXT,
  ip_address INET,
  country_code TEXT,
  city TEXT,
  bounce BOOLEAN default false,
  converted BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.user_sessions ENABLE row LEVEL SECURITY;

-- user_journeys
create table if not exists public.user_journeys (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID,
  anonymous_id TEXT,
  session_id TEXT,
  journey_type TEXT not null check (
    journey_type in (
      'product_discovery',
      'purchase_funnel',
      'onboarding',
      'support',
      'content_engagement'
    )
  ),
  journey_step TEXT not null,
  step_order INTEGER not null,
  page_url TEXT,
  action_taken TEXT,
  time_spent INTEGER,
  completed BOOLEAN default false,
  dropped_off BOOLEAN default false,
  conversion_value DECIMAL(10, 2),
  properties JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.user_journeys ENABLE row LEVEL SECURITY;

-- performance_metrics
create table if not exists public.performance_metrics (
  id UUID primary key default uuid_generate_v4 (),
  session_id TEXT not null,
  page_url TEXT not null,
  lcp DECIMAL(8, 2),
  fid DECIMAL(8, 2),
  cls DECIMAL(6, 4),
  fcp DECIMAL(8, 2),
  ttfb DECIMAL(8, 2),
  dns_lookup_time INTEGER,
  tcp_connect_time INTEGER,
  tls_setup_time INTEGER,
  request_time INTEGER,
  response_time INTEGER,
  dom_processing_time INTEGER,
  load_event_time INTEGER,
  custom_metrics JSONB default '{}',
  created_at TIMESTAMPTZ default NOW()
);

alter table public.performance_metrics ENABLE row LEVEL SECURITY;

-- addresses
create table if not exists public.addresses (
  id UUID primary key default uuid_generate_v4 (),
  user_id UUID not null references auth.users (id) on delete CASCADE,
  type TEXT not null check (type in ('shipping', 'billing')),
  first_name TEXT not null,
  last_name TEXT not null,
  address TEXT not null,
  city TEXT not null,
  postal_code TEXT not null,
  country TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW()
);

alter table public.addresses ENABLE row LEVEL SECURITY;

-- reviews - Updated to reference external API product IDs
create table if not exists public.reviews (
  id UUID primary key default uuid_generate_v4 (),
  product_id integer not null, -- Changed from UUID to INTEGER for external API
  user_id UUID not null references auth.users (id) on delete CASCADE,
  rating INTEGER not null check (
    rating >= 1
    and rating <= 5
  ),
  comment TEXT not null,
  created_at TIMESTAMPTZ default NOW(),
  unique (product_id, user_id)
);

alter table public.reviews ENABLE row LEVEL SECURITY;

-- newsletter_subscriptions
create table if not exists public.newsletter_subscriptions (
  id UUID primary key default uuid_generate_v4 (),
  email TEXT not null unique,
  subscribed_at TIMESTAMPTZ default NOW(),
  updated_at TIMESTAMPTZ default NOW() -- Added missing timestamp
);

alter table public.newsletter_subscriptions ENABLE row LEVEL SECURITY;

-- order_status_history (NEW TABLE)
create table if not exists public.order_status_history (
  id UUID primary key default uuid_generate_v4 (),
  order_id UUID not null,
  old_status TEXT,
  new_status TEXT not null,
  changed_by UUID references auth.users (id),
  notes TEXT,
  created_at TIMESTAMPTZ default NOW()
);

-- =================================================================
-- Indexes
-- =================================================================
create unique INDEX IF not exists anonymous_cart_items_pkey on public.anonymous_cart_items using btree (id);

create unique INDEX IF not exists anonymous_carts_pkey on public.anonymous_carts using btree (id);

create unique INDEX IF not exists anonymous_carts_session_id_key on public.anonymous_carts using btree (session_id);

create unique INDEX IF not exists cart_items_pkey on public.cart_items using btree (id);

create unique INDEX IF not exists carts_pkey on public.carts using btree (id);

create unique INDEX IF not exists carts_user_id_key on public.carts (user_id);

-- Added unique constraint
create index IF not exists idx_anonymous_cart_items_cart_id on public.anonymous_cart_items using btree (cart_id);

create index IF not exists idx_anonymous_cart_items_product_id on public.anonymous_cart_items using btree (product_id);

create index IF not exists idx_anonymous_cart_items_variant_id on public.anonymous_cart_items using btree (variant_id)
where
  (variant_id is not null);

create index IF not exists idx_anonymous_carts_email on public.anonymous_carts using btree (email)
where
  (email is not null);

create index IF not exists idx_anonymous_carts_expires_at on public.anonymous_carts using btree (expires_at);

create index IF not exists idx_anonymous_carts_session_id on public.anonymous_carts using btree (session_id);

create index IF not exists idx_anonymous_carts_status on public.anonymous_carts using btree (status);

create index IF not exists idx_anonymous_carts_utm_source on public.anonymous_carts using btree (utm_source)
where
  (utm_source is not null);

create unique INDEX IF not exists order_items_pkey on public.order_items using btree (id);

create unique INDEX IF not exists orders_pkey on public.orders using btree (id);

create unique INDEX IF not exists profiles_pkey on public.profiles using btree (id);

-- Composite indexes for performance
create index IF not exists idx_anonymous_carts_status_created_at on public.anonymous_carts (status, created_at);

create index IF not exists idx_orders_user_status on public.orders (user_id, status)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_session_event on public.experience_tracks (session_id, event_type, created_at);

-- GIN indexes for JSONB columns
create index IF not exists idx_anonymous_carts_cart_data_gin on public.anonymous_carts using GIN (cart_data);

create index IF not exists idx_experience_tracks_properties_gin on public.experience_tracks using GIN (custom_properties);

-- Missing foreign key indexes
create index IF not exists idx_cart_items_cart_id on public.cart_items (cart_id);

create index IF not exists idx_cart_items_product_id on public.cart_items (product_id);

create index IF not exists idx_cart_items_variant_id on public.cart_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_order_items_order_id on public.order_items (order_id);

create index IF not exists idx_order_items_product_id on public.order_items (product_id);

create index IF not exists idx_order_items_variant_id on public.order_items (variant_id)
where
  variant_id is not null;

create index IF not exists idx_carts_user_id on public.carts (user_id);

-- Unique constraint for cart items
create unique INDEX IF not exists cart_items_cart_product_variant_key on public.cart_items (
  cart_id,
  product_id,
  COALESCE(
    variant_id,
    0
  )
);

-- Additional indexes from original
create index IF not exists idx_experience_tracks_session_id on public.experience_tracks (session_id);

create index IF not exists idx_experience_tracks_user_id on public.experience_tracks (user_id)
where
  user_id is not null;

create index IF not exists idx_experience_tracks_anonymous_id on public.experience_tracks (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_experience_tracks_event_type on public.experience_tracks (event_type);

create index IF not exists idx_experience_tracks_page_url on public.experience_tracks (page_url);

create index IF not exists idx_experience_tracks_created_at on public.experience_tracks (created_at);

create index IF not exists idx_user_sessions_session_id on public.user_sessions (session_id);

create index IF not exists idx_user_sessions_user_id on public.user_sessions (user_id)
where
  user_id is not null;

create index IF not exists idx_user_sessions_started_at on public.user_sessions (started_at);

create index IF not exists idx_user_journeys_user_id on public.user_journeys (user_id)
where
  user_id is not null;

create index IF not exists idx_user_journeys_anonymous_id on public.user_journeys (anonymous_id)
where
  anonymous_id is not null;

create index IF not exists idx_user_journeys_journey_type on public.user_journeys (journey_type);

create index IF not exists idx_user_journeys_session_id on public.user_journeys (session_id);

create index IF not exists idx_performance_metrics_session_id on public.performance_metrics (session_id);

create index IF not exists idx_performance_metrics_page_url on public.performance_metrics (page_url);

create index IF not exists idx_performance_metrics_created_at on public.performance_metrics (created_at);

create index IF not exists idx_anonymous_carts_updated_at on public.anonymous_carts (updated_at);

create index IF not exists idx_orders_anonymous_cart_id on public.orders (anonymous_cart_id)
where
  anonymous_cart_id is not null;

create index IF not exists idx_orders_status on public.orders (status);

create index IF not exists idx_orders_created_at on public.orders (created_at);

create index IF not exists idx_orders_user_id on public.orders (user_id)
where
  user_id is not null;

create index IF not exists idx_addresses_user_id on public.addresses (user_id);

create index IF not exists idx_reviews_product_id on public.reviews (product_id);

create index IF not exists idx_reviews_user_id on public.reviews (user_id);

create index IF not exists idx_order_status_history_order_id on public.order_status_history (order_id);

-- =================================================================
-- Primary Keys & Foreign Keys & Constraints
-- =================================================================
-- Primary Keys
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_pkey" primary key using INDEX "anonymous_cart_items_pkey";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_pkey" primary key using INDEX "anonymous_carts_pkey";

alter table "public"."cart_items"
add constraint "cart_items_pkey" primary key using INDEX "cart_items_pkey";

alter table "public"."carts"
add constraint "carts_pkey" primary key using INDEX "carts_pkey";

alter table "public"."order_items"
add constraint "order_items_pkey" primary key using INDEX "order_items_pkey";

alter table "public"."orders"
add constraint "orders_pkey" primary key using INDEX "orders_pkey";

alter table "public"."profiles"
add constraint "profiles_pkey" primary key using INDEX "profiles_pkey";

-- Foreign Keys & Constraints
alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_cart_id_fkey" foreign KEY (cart_id) references anonymous_carts (id) on delete CASCADE;

alter table "public"."anonymous_cart_items"
add constraint "anonymous_cart_items_quantity_check" check ((quantity > 0));

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_session_id_key" unique using INDEX "anonymous_carts_session_id_key";

alter table "public"."anonymous_carts"
add constraint "anonymous_carts_status_check" check (
  (
    (
      status = any (
        array[
          'active'::text,
          'abandoned'::text,
          'converted'::text,
          'expired'::text
        ]
      )
    )
  )
);

alter table "public"."cart_items"
add constraint "cart_items_cart_id_fkey" foreign KEY (cart_id) references carts (id) on delete CASCADE;

alter table "public"."carts"
add constraint "carts_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."order_items"
add constraint "order_items_order_id_fkey" foreign KEY (order_id) references orders (id) on delete CASCADE;

alter table "public"."orders"
alter column user_id
drop not null;

alter table "public"."orders"
add constraint "orders_anonymous_cart_id_fkey" foreign KEY (anonymous_cart_id) references public.anonymous_carts (id) on delete set null deferrable initially DEFERRED;

alter table "public"."orders"
add constraint "orders_user_id_fkey" foreign KEY (user_id) references profiles (id) on delete CASCADE;

alter table "public"."orders"
add constraint orders_user_or_anonymous_check check (
  (
    (user_id is not null)
    or (anonymous_cart_id is not null)
  )
);

alter table "public"."profiles"
add constraint "profiles_id_fkey" foreign KEY (id) references auth.users (id) on delete CASCADE;

-- Check constraints for data integrity
alter table public.order_items
add constraint order_items_price_positive check (price >= 0),
add constraint order_items_quantity_positive check (quantity > 0);

-- Email validation constraints
alter table public.anonymous_carts
add constraint anonymous_carts_email_valid check (
  email is null
  or email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

alter table public.newsletter_subscriptions
add constraint newsletter_subscriptions_email_valid check (
  email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
);

-- =================================================================
-- Functions
-- =================================================================
create or replace function public.update_updated_at_column () RETURNS trigger LANGUAGE plpgsql as $function$ BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 $function$;

create or replace function public.get_cart_analytics (
  p_start_date timestamp with time zone,
  p_end_date timestamp with time zone
) RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            DATE(created_at) AS date,
            COUNT(*) FILTER (WHERE status = 'active') AS active_carts,
            COUNT(*) FILTER (WHERE status = 'abandoned') AS abandoned_carts,
            COUNT(*) FILTER (WHERE status = 'converted') AS converted_carts,
            AVG(total_value) FILTER (WHERE status = 'converted') AS avg_cart_value,
            AVG(item_count) FILTER (WHERE status = 'converted') AS avg_items_per_cart
        FROM public.anonymous_carts
        WHERE created_at BETWEEN p_start_date AND p_end_date
        GROUP BY DATE(created_at)
    )
    SELECT 
        ds.date,
        COALESCE(ds.active_carts, 0)::INTEGER,
        COALESCE(ds.abandoned_carts, 0)::INTEGER,
        COALESCE(ds.converted_carts, 0)::INTEGER,
        COALESCE(ds.avg_cart_value, 0)::NUMERIC(10,2),
        COALESCE(ds.avg_items_per_cart, 0)::NUMERIC(10,2)
    FROM daily_stats ds
    ORDER BY ds.date;
END;
 $function$;

create or replace function public.get_cart_analytics () RETURNS table (
  date DATE,
  active_carts INTEGER,
  abandoned_carts INTEGER,
  converted_carts INTEGER,
  avg_cart_value NUMERIC(10, 2),
  avg_items_per_cart NUMERIC(10, 2)
) LANGUAGE plpgsql as $function$ BEGIN
    RETURN QUERY SELECT * FROM public.get_cart_analytics(
        (NOW() - INTERVAL '30 days'),
        NOW()
    );
END;
 $function$;

create or replace function public.mark_abandoned_carts (abandonment_minutes INTEGER default 30) RETURNS INTEGER LANGUAGE plpgsql as $function$ DECLARE
    updated_count INTEGER;
BEGIN
    WITH abandoned_carts AS (
        UPDATE public.anonymous_carts
        SET status = 'abandoned',
            updated_at = NOW()
        WHERE status = 'active'
        AND updated_at < (NOW() - (abandonment_minutes * INTERVAL '1 minute'))
        RETURNING 1
    )
    SELECT COUNT(*) INTO updated_count FROM abandoned_carts;
    
    RETURN updated_count;
END;
 $function$;

create or replace function public.update_cart_totals (p_cart_id UUID) RETURNS VOID as $$ BEGIN
    UPDATE public.anonymous_carts ac
    SET 
        item_count = COALESCE(totals.total_qty, 0),
        total_value = COALESCE(totals.total_val, 0),
        updated_at = NOW()
    FROM (
        SELECT 
            SUM(quantity) as total_qty,
            SUM(price * quantity) as total_val
        FROM public.anonymous_cart_items 
        WHERE cart_id = p_cart_id
    ) AS totals
    WHERE ac.id = p_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.trigger_update_cart_totals () RETURNS TRIGGER as $$ BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM public.update_cart_totals(OLD.cart_id);
        RETURN OLD;
    ELSE
        PERFORM public.update_cart_totals(NEW.cart_id);
        RETURN NEW;
    END IF;
END;
 $$ LANGUAGE plpgsql;

create or replace function update_session_stats () RETURNS TRIGGER as $$ BEGIN
    INSERT INTO public.user_sessions (
        session_id, user_id, anonymous_id, started_at, entry_url, entry_page_title,
        user_agent, device_type, browser_name, os_name,
        utm_source, utm_medium, utm_campaign, referrer_url,
        ip_address, country_code, city, page_views, interactions
    )
    VALUES (
        NEW.session_id, NEW.user_id, NEW.anonymous_id, NEW.created_at, NEW.page_url, NEW.page_title,
        NEW.user_agent, NEW.device_type, NEW.browser_name, NEW.os_name,
        NEW.utm_source, NEW.utm_medium, NEW.utm_campaign, NEW.referrer_url,
        NEW.ip_address, NEW.country_code, NEW.city, 
        CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END
    )
    ON CONFLICT (session_id) DO UPDATE SET
        user_id = COALESCE(NEW.user_id, user_sessions.user_id),
        ended_at = NEW.created_at,
        exit_url = NEW.page_url,
        exit_page_title = NEW.page_title,
        page_views = user_sessions.page_views + CASE WHEN NEW.event_type = 'page_view' THEN 1 ELSE 0 END,
        interactions = user_sessions.interactions + CASE WHEN NEW.event_type != 'page_view' THEN 1 ELSE 0 END,
        duration = EXTRACT(EPOCH FROM (NEW.created_at - user_sessions.started_at))::INTEGER,
        updated_at = NOW();

    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

create or replace function mark_bounce_sessions () RETURNS INTEGER as $$ DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.user_sessions 
    SET bounce = TRUE, updated_at = NOW()
    WHERE page_views <= 1 
      AND duration < 30 
      AND bounce = FALSE
      AND ended_at < (NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function calculate_funnel_conversion (
  p_journey_type TEXT,
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '30 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  step TEXT,
  step_order INTEGER,
  users BIGINT,
  conversion_rate DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH funnel_steps AS (
        SELECT 
            journey_step,
            step_order,
            COUNT(DISTINCT COALESCE(user_id::TEXT, anonymous_id)) as step_users
        FROM public.user_journeys
        WHERE journey_type = p_journey_type
          AND created_at BETWEEN p_start_date AND p_end_date
        GROUP BY journey_step, step_order
        ORDER BY step_order
    ),
    first_step AS (
        SELECT step_users as first_step_users
        FROM funnel_steps
        ORDER BY step_order
        LIMIT 1
    )
    SELECT 
        fs.journey_step,
        fs.step_order,
        fs.step_users,
        CASE 
            WHEN fst.first_step_users > 0 THEN 
                ROUND((fs.step_users::DECIMAL / fst.first_step_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    CROSS JOIN first_step fst
    ORDER BY fs.step_order;
END;
 $$ LANGUAGE plpgsql;

create or replace function get_user_behavior_insights (
  p_start_date TIMESTAMPTZ default (NOW() - INTERVAL '7 days'),
  p_end_date TIMESTAMPTZ default NOW()
) RETURNS table (
  metric_name TEXT,
  metric_value DECIMAL,
  metric_unit TEXT,
  comparison_period_value DECIMAL,
  change_percentage DECIMAL
) as $$ BEGIN
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN p_start_date AND p_end_date
    ),
    previous_period AS (
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(CASE WHEN event_type = 'page_view' THEN time_on_page END) as avg_time_on_page,
            AVG(scroll_depth) as avg_scroll_depth
        FROM public.experience_tracks
        WHERE created_at BETWEEN 
            p_start_date - (p_end_date - p_start_date) AND 
            p_start_date
    )
    SELECT 
        'Total Sessions'::TEXT,
        cp.total_sessions::DECIMAL,
        'count'::TEXT,
        pp.total_sessions::DECIMAL,
        CASE WHEN pp.total_sessions > 0 THEN ROUND(((cp.total_sessions - pp.total_sessions)::DECIMAL / pp.total_sessions) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Time on Page'::TEXT,
        ROUND(cp.avg_time_on_page, 2),
        'seconds'::TEXT,
        ROUND(pp.avg_time_on_page, 2),
        CASE WHEN pp.avg_time_on_page > 0 THEN ROUND(((cp.avg_time_on_page - pp.avg_time_on_page) / pp.avg_time_on_page) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp
    UNION ALL
    SELECT 
        'Average Scroll Depth'::TEXT,
        ROUND(cp.avg_scroll_depth, 2),
        'percentage'::TEXT,
        ROUND(pp.avg_scroll_depth, 2),
        CASE WHEN pp.avg_scroll_depth > 0 THEN ROUND(((cp.avg_scroll_depth - pp.avg_scroll_depth) / pp.avg_scroll_depth) * 100, 2) ELSE 0 END
    FROM current_period cp, previous_period pp;
END;
 $$ LANGUAGE plpgsql;

create or replace function cleanup_old_experience_data () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.experience_tracks WHERE created_at < (NOW() - INTERVAL '90 days');
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    DELETE FROM public.user_sessions WHERE created_at < (NOW() - INTERVAL '90 days');
    DELETE FROM public.performance_metrics WHERE created_at < (NOW() - INTERVAL '30 days');
    DELETE FROM public.user_journeys WHERE created_at < (NOW() - INTERVAL '90 days');
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.cleanup_expired_carts () RETURNS INTEGER as $$ DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM public.anonymous_carts
        WHERE expires_at < NOW()
        RETURNING 1
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.migrate_anonymous_to_user_cart (p_session_id TEXT, p_user_id UUID) RETURNS UUID as $$ DECLARE
    v_cart_id UUID;
    v_anonymous_cart_id UUID;
BEGIN
    -- Validate inputs
    IF p_session_id IS NULL OR p_user_id IS NULL THEN
        RAISE EXCEPTION 'Session ID and User ID are required';
    END IF;
    
    SELECT id INTO v_anonymous_cart_id
    FROM public.anonymous_carts
    WHERE session_id = p_session_id
    AND status = 'active';
    
    IF v_anonymous_cart_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    INSERT INTO public.carts (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id)
    DO UPDATE SET updated_at = NOW()
    RETURNING id INTO v_cart_id;
    
    INSERT INTO public.cart_items (cart_id, product_id, variant_id, quantity)
    SELECT v_cart_id, product_id, variant_id, quantity
    FROM public.anonymous_cart_items
    WHERE cart_id = v_anonymous_cart_id
    ON CONFLICT (cart_id, product_id, variant_id) 
    DO UPDATE SET 
        quantity = cart_items.quantity + EXCLUDED.quantity,
        updated_at = NOW();
    
    UPDATE public.anonymous_carts
    SET status = 'converted',
        updated_at = NOW()
    WHERE id = v_anonymous_cart_id;
    
    RETURN v_cart_id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.get_cart_by_session (p_session_id TEXT) RETURNS table (
  cart_id UUID,
  session_id TEXT,
  status TEXT,
  item_count INTEGER,
  total_value DECIMAL(10, 2),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) as $$ BEGIN
    RETURN QUERY
    SELECT 
        ac.id AS cart_id,
        ac.session_id,
        ac.status,
        COALESCE(SUM(aci.quantity), 0)::INTEGER AS item_count,
        COALESCE(SUM(aci.price * aci.quantity), 0)::DECIMAL(10,2) AS total_value,
        ac.created_at,
        ac.updated_at
    FROM public.anonymous_carts ac
    LEFT JOIN public.anonymous_cart_items aci ON ac.id = aci.cart_id
    WHERE ac.session_id = p_session_id
    GROUP BY ac.id;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.schedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN PERFORM cron.schedule('mark-abandoned-carts', '0 * * * *', 'SELECT public.mark_abandoned_carts(30)'); PERFORM cron.schedule('cleanup-expired-carts', '0 3 * * *', 'SELECT public.cleanup_expired_carts()'); END; $$ LANGUAGE plpgsql;

create or replace function public.unschedule_cart_cleanup_jobs () RETURNS VOID as $$ BEGIN
    PERFORM cron.unschedule('mark-abandoned-carts');
    PERFORM cron.unschedule('cleanup-expired-carts');
END;
 $$ LANGUAGE plpgsql;

create or replace function public.recover_abandoned_cart (p_session_id TEXT) RETURNS BOOLEAN as $$ DECLARE
    v_updated_rows INTEGER;
BEGIN
    UPDATE public.anonymous_carts
    SET status = 'active',
        updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'abandoned';
    
    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;
    RETURN v_updated_rows > 0;
END;
 $$ LANGUAGE plpgsql;

create or replace function public.create_anonymous_order (
  p_anonymous_cart_id UUID,
  p_shipping_address JSONB,
  p_billing_address JSONB,
  p_payment_method TEXT,
  p_status TEXT default 'pending'
) RETURNS UUID as $$ DECLARE
    v_order_id UUID;
    v_cart_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_anonymous_cart_id IS NULL OR p_shipping_address IS NULL OR p_payment_method IS NULL THEN
        RAISE EXCEPTION 'Cart ID, shipping address, and payment method are required';
    END IF;
    
    SELECT EXISTS (
        SELECT 1
        FROM public.anonymous_carts
        WHERE id = p_anonymous_cart_id AND status = 'active'
    ) INTO v_cart_exists;

    IF NOT v_cart_exists THEN
        RAISE EXCEPTION 'Invalid or inactive anonymous cart';
    END IF;

    INSERT INTO public.orders (anonymous_cart_id, status, shipping_address, billing_address, payment_method, created_at, updated_at, total)
    VALUES (p_anonymous_cart_id, p_status, p_shipping_address, p_billing_address, p_payment_method, NOW(), NOW(), (SELECT total_value FROM public.anonymous_carts WHERE id = p_anonymous_cart_id))
    RETURNING id INTO v_order_id;

    UPDATE public.anonymous_carts
    SET status = 'converted', updated_at = NOW()
    WHERE id = p_anonymous_cart_id;

    RETURN v_order_id;
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

create or replace function public.get_order_with_cart (p_order_id UUID) RETURNS JSONB as $$ DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'order_id', o.id,
        'status', o.status,
        'created_at', o.created_at,
        'updated_at', o.updated_at,
        'shipping_address', o.shipping_address,
        'billing_address', o.billing_address,
        'payment_method', o.payment_method,
        'is_guest_order', o.user_id IS NULL,
        'cart', CASE
            WHEN o.anonymous_cart_id IS NOT NULL THEN (
                SELECT jsonb_build_object(
                    'cart_id', ac.id,
                    'session_id', ac.session_id,
                    'created_at', ac.created_at,
                    'items', COALESCE((
                        SELECT jsonb_agg(jsonb_build_object(
                            'product_id', aci.product_id,
                            'variant_id', aci.variant_id,
                            'product_title', aci.product_title,
                            'product_image', aci.product_image,
                            'price', aci.price,
                            'quantity', aci.quantity
                        ))
                        FROM public.anonymous_cart_items aci
                        WHERE aci.cart_id = ac.id
                    ), '[]'::jsonb)
                )
                FROM public.anonymous_carts ac
                WHERE ac.id = o.anonymous_cart_id
            )
            ELSE NULL
        END,
        'user', CASE
            WHEN o.user_id IS NOT NULL THEN (
                SELECT jsonb_build_object('id', u.id, 'email', u.email)
                FROM auth.users u
                WHERE u.id = o.user_id
            )
            ELSE NULL
        END
    ) INTO v_result
    FROM public.orders o
    WHERE o.id = p_order_id;
    RETURN v_result;
END;
 $$ LANGUAGE plpgsql STABLE;

create or replace function public.sync_order_cart_status () RETURNS TRIGGER as $$ BEGIN
    IF NEW.status = 'converted' AND OLD.status != 'converted' THEN
        UPDATE public.orders
        SET status = 'processing', updated_at = NOW()
        WHERE anonymous_cart_id = NEW.id AND status = 'pending';
    END IF;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

-- Rate limiting function
create or replace function check_rate_limit (p_ip_address INET) RETURNS BOOLEAN as $$ DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM public.experience_tracks
    WHERE ip_address = p_ip_address
    AND created_at > NOW() - INTERVAL '1 minute';
    
    RETURN request_count < 100; -- Max 100 requests per minute
END;
 $$ LANGUAGE plpgsql SECURITY DEFINER;

-- =================================================================
-- Triggers
-- =================================================================
drop trigger IF exists trigger_update_anonymous_cart_items_updated_at on public.anonymous_cart_items;

create trigger trigger_update_anonymous_cart_items_updated_at BEFORE
update on public.anonymous_cart_items for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_cart_totals_on_delete on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_delete
after DELETE on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_insert on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_insert
after INSERT on public.anonymous_cart_items for EACH row
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_cart_totals_on_update on public.anonymous_cart_items;

create trigger trigger_update_cart_totals_on_update
after
update on public.anonymous_cart_items for EACH row when (
  OLD.quantity is distinct from NEW.quantity
  or OLD.price is distinct from NEW.price
)
execute FUNCTION public.trigger_update_cart_totals ();

drop trigger IF exists trigger_update_anonymous_carts_updated_at on public.anonymous_carts;

create trigger trigger_update_anonymous_carts_updated_at BEFORE
update on public.anonymous_carts for EACH row
execute FUNCTION update_updated_at_column ();

drop trigger IF exists trigger_update_session_stats on public.experience_tracks;

create trigger trigger_update_session_stats
after INSERT on public.experience_tracks for EACH row
execute FUNCTION update_session_stats ();

drop trigger IF exists trg_sync_order_cart_status on public.anonymous_carts;

create trigger trg_sync_order_cart_status
after
update OF status on public.anonymous_carts for EACH row when (OLD.status is distinct from NEW.status)
execute FUNCTION public.sync_order_cart_status ();

-- Trigger for order_items updated_at
drop trigger IF exists trigger_update_order_items_updated_at on public.order_items;

create trigger trigger_update_order_items_updated_at BEFORE
update on public.order_items for EACH row
execute FUNCTION update_updated_at_column ();

-- Trigger for newsletter_subscriptions updated_at
drop trigger IF exists trigger_update_newsletter_subscriptions_updated_at on public.newsletter_subscriptions;

create trigger trigger_update_newsletter_subscriptions_updated_at BEFORE
update on public.newsletter_subscriptions for EACH row
execute FUNCTION update_updated_at_column ();

-- =================================================================
-- RLS Policies
-- =================================================================
-- Policies for anonymous_cart_items
drop policy IF EXISTS "Allow anonymous access to own cart items" ON "public"."anonymous_cart_items";

CREATE POLICY "Allow service role full access to anonymous_cart_items" ON "public"."anonymous_cart_items" AS PERMISSIVE FOR ALL TO public USING ((auth.role() = 'service_role'::text));

CREATE POLICY "Allow access to cart items by session" ON public.anonymous_cart_items FOR ALL USING (
  cart_id IN (
    SELECT id FROM public.anonymous_carts 
    WHERE session_id = current_setting('app.current_session_id', true)::TEXT
  )
);

-- Policies for anonymous_carts
CREATE POLICY "Allow anonymous access to own cart" ON "public"."anonymous_carts" AS PERMISSIVE FOR ALL TO public USING ((auth.role() = 'anon'::text));

CREATE POLICY "Allow service role full access to anonymous_carts" ON "public"."anonymous_carts" AS PERMISSIVE FOR ALL TO public USING ((auth.role() = 'service_role'::text));

CREATE POLICY "Allow public access with session check" ON public.anonymous_carts FOR ALL USING (true);

-- Policies for cart_items
CREATE POLICY "Cart items are viewable by cart owner." ON "public"."cart_items" AS PERMISSIVE FOR SELECT TO public USING (
  EXISTS (SELECT 1 FROM carts WHERE (carts.id = cart_items.cart_id AND carts.user_id = auth.uid()))
);

CREATE POLICY "Users can delete cart items from their cart." ON "public"."cart_items" AS PERMISSIVE FOR DELETE TO public USING (
  EXISTS (SELECT 1 FROM carts WHERE (carts.id = cart_items.cart_id AND carts.user_id = auth.uid()))
);

CREATE POLICY "Users can insert cart items for their cart." ON "public"."cart_items" AS PERMISSIVE FOR INSERT TO public WITH CHECK (
  EXISTS (SELECT 1 FROM carts WHERE (carts.id = cart_items.cart_id AND carts.user_id = auth.uid()))
);

CREATE POLICY "Users can update cart items for their cart." ON "public"."cart_items" AS PERMISSIVE FOR UPDATE TO public USING (
  EXISTS (SELECT 1 FROM carts WHERE (carts.id = cart_items.cart_id AND carts.user_id = auth.uid()))
);

-- Policies for carts
CREATE POLICY "Users can create their own cart." ON "public"."carts" AS PERMISSIVE FOR INSERT TO public WITH CHECK ((auth.uid() = user_id));

CREATE POLICY "Users can update their own cart." ON "public"."carts" AS PERMISSIVE FOR UPDATE TO public USING ((auth.uid() = user_id));

CREATE POLICY "Users can view their own cart." ON "public"."carts" AS PERMISSIVE FOR SELECT TO public USING ((auth.uid() = user_id));

-- Policies for order_items
CREATE POLICY "Order items are viewable by order owner." ON "public"."order_items" AS PERMISSIVE FOR SELECT TO public USING (
  EXISTS (SELECT 1 FROM orders WHERE (orders.id = order_items.order_id AND orders.user_id = auth.uid()))
);

CREATE POLICY "Users can insert order items for their orders." ON "public"."order_items" AS PERMISSIVE FOR INSERT TO public WITH CHECK (
  EXISTS (SELECT 1 FROM orders WHERE (orders.id = order_items.order_id AND orders.user_id = auth.uid()))
);

-- Policies for orders
CREATE POLICY "Users can create orders" ON public.orders FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own orders" ON public.orders FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Allow anonymous order creation" ON public.orders FOR INSERT WITH CHECK ((anonymous_cart_id IS NOT NULL AND user_id IS NULL));

DROP POLICY IF EXISTS "Users can update their own orders" ON public.orders;

CREATE POLICY "Users can update their own orders" ON public.orders FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Policies for profiles
CREATE POLICY "Public profiles are viewable by everyone." ON "public"."profiles" AS PERMISSIVE FOR SELECT TO public USING (true);

CREATE POLICY "Users can insert their own profile." ON "public"."profiles" AS PERMISSIVE FOR INSERT TO public WITH CHECK ((auth.uid() = id));

CREATE POLICY "Users can update their own profile." ON "public"."profiles" AS PERMISSIVE FOR UPDATE TO public USING ((auth.uid() = id));

-- Policies for experience_tracks
CREATE POLICY "Allow service role full access to experience_tracks" ON public.experience_tracks FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated access to experience_tracks" ON public.experience_tracks FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow anonymous access to experience_tracks" ON public.experience_tracks FOR INSERT WITH CHECK (auth.role() = 'anon');

-- Policies for user_sessions
CREATE POLICY "Allow service role full access to user_sessions" ON public.user_sessions FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated access to user_sessions" ON public.user_sessions FOR ALL USING (auth.role() = 'authenticated');

-- Policies for user_journeys
CREATE POLICY "Allow service role full access to user_journeys" ON public.user_journeys FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated access to user_journeys" ON public.user_journeys FOR ALL USING (auth.role() = 'authenticated');

-- Policies for performance_metrics
CREATE POLICY "Allow service role full access to performance_metrics" ON public.performance_metrics FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated access to performance_metrics" ON public.performance_metrics FOR ALL USING (auth.role() = 'authenticated');

-- Policies for addresses
CREATE POLICY "Users can view their own addresses" ON public.addresses FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own addresses" ON public.addresses FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own addresses" ON public.addresses FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own addresses" ON public.addresses FOR DELETE USING (auth.uid() = user_id);

-- Policies for reviews
CREATE POLICY "Reviews are public" ON public.reviews FOR SELECT USING (true);

CREATE POLICY "Users can insert their own reviews" ON public.reviews FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reviews" ON public.reviews FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reviews" ON public.reviews FOR DELETE USING (auth.uid() = user_id);

-- Policies for newsletter_subscriptions
CREATE POLICY "Public can subscribe to newsletter" ON public.newsletter_subscriptions FOR INSERT WITH CHECK (true);

CREATE POLICY "Service roles can manage subscriptions" ON public.newsletter_subscriptions FOR ALL USING (auth.role() = 'service_role');

-- Policies for order_status_history
CREATE POLICY "Order status history is viewable by order owner" ON public.order_status_history FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.orders o 
    WHERE o.id = order_status_history.order_id AND o.user_id = auth.uid()
  )
);

CREATE POLICY "Service role can manage order status history" ON public.order_status_history FOR ALL USING (auth.role() = 'service_role');

-- =================================================================
-- Comments
-- =================================================================
COMMENT on table public.anonymous_carts is 'Stores anonymous shopping carts for users who are not logged in';

COMMENT on column public.anonymous_carts.status is 'Status of the cart: active, abandoned, converted, or expired';

COMMENT on column public.anonymous_carts.utm_source is 'UTM source parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_medium is 'UTM medium parameter for tracking marketing campaigns';

COMMENT on column public.anonymous_carts.utm_campaign is 'UTM campaign parameter for tracking marketing campaigns';

COMMENT on FUNCTION public.mark_abandoned_carts (INTEGER) is 'Marks carts as abandoned after a specified period of inactivity (default 30 minutes)';

COMMENT on FUNCTION public.cleanup_expired_carts () is 'Removes expired carts from the database. Replaces cleanup_expired_anonymous_carts.';

COMMENT on FUNCTION public.migrate_anonymous_to_user_cart (TEXT, UUID) is 'Transfers an anonymous cart to a user account when they log in';

COMMENT on FUNCTION public.get_cart_by_session (TEXT) is 'Retrieves cart summary by session ID';

COMMENT on FUNCTION public.update_cart_totals (UUID) is 'Updates the item count and total value for a cart';

COMMENT on table public.experience_tracks is 'Detailed tracking of user interactions and behavior';

COMMENT on table public.user_sessions is 'Session-level aggregated data for user visits';

COMMENT on table public.user_journeys is 'User journey and funnel tracking for conversion analysis';

COMMENT on table public.performance_metrics is 'Core Web Vitals and performance metrics tracking';

COMMENT on FUNCTION update_session_stats () is 'Automatically updates session statistics when experience tracks are added';

COMMENT on FUNCTION mark_bounce_sessions () is 'Identifies and marks bounce sessions based on behavior';

COMMENT on FUNCTION calculate_funnel_conversion (TEXT, TIMESTAMPTZ, TIMESTAMPTZ) is 'Calculates conversion rates for user journey funnels';

COMMENT on FUNCTION get_user_behavior_insights (TIMESTAMPTZ, TIMESTAMPTZ) is 'Provides behavioral insights with period-over-period comparison';

COMMENT on FUNCTION cleanup_old_experience_data () is 'Cleans up old tracking data to manage database size';

COMMENT on column public.orders.anonymous_cart_id is 'Reference to the anonymous cart for guest checkouts';

COMMENT on constraint orders_user_or_anonymous_check on public.orders is 'Ensures that either user_id or anonymous_cart_id is provided';

COMMENT on FUNCTION public.create_anonymous_order is 'Creates an order from an anonymous cart for guest checkouts';

COMMENT on FUNCTION public.get_order_with_cart is 'Retrieves order details with associated cart information';

COMMENT on table public.addresses is 'Stores shipping and billing addresses for users.';

COMMENT on table public.reviews is 'Stores customer reviews for products.';

COMMENT on table public.newsletter_subscriptions is 'Stores email addresses for newsletter subscribers.';

COMMENT on table public.order_status_history is 'Tracks changes to order status over time.';
```

