# 🛍️ Shopify + Next.js Integration

**Chat ID:** `ed0daccb-f446-4772-a15f-f7eb5466c422`
**Created At:** 1970-01-21 08:21:57
**Updated At:** 1970-01-21 08:22:08

## Chat History

### User:
You are a LLM Prompt Generator.
```md
Shopify Provider

Demo: https://shopify.demo.vercel.store/

Before getting started, a Shopify account and store is required before using the provider.

Next, copy the .env.template file in this directory to .env.local in the main directory (which will be ignored by Git):

cp packages/shopify/.env.template .env.local

Then, set the environment variables in .env.local to match the ones from your store.
Contribute

Our commitment to Open Source can be found here.

If you find an issue with the provider or want a new feature, feel free to open a PR or create a new issue.
Modifications

These modifications are temporarily until contributions are made to remove them.
Adding item to Cart

// components/product/ProductView/ProductView.tsx
const ProductView: FC<Props> = ({ product }) => {
  const addToCart = async () => {
    setLoading(true)
    try {
      await addItem({
        productId: product.id,
        variantId: variant ? variant.id : product.variants[0].id,
      })
      openSidebar()
      setLoading(false)
    } catch (err) {
      setLoading(false)
    }
  }
}

Proceed to Checkout

// components/cart/CartSidebarView/CartSidebarView.tsx
import { useCommerce } from '@framework'

const CartSidebarView: FC = () => {
  const { checkout } = useCommerce()
  return (
    <Button href={checkout.webUrl} Component="a" width="100%">
      Proceed to Checkout
    </Button>
  )
}

APIs

Collections of APIs to fetch data from a Shopify store.

The data is fetched using the Shopify JavaScript Buy SDK. Read the Shopify Storefront API reference for more information.
getProduct

Get a single product by its handle.

import getProduct from '@framework/product/get-product'
import { getConfig } from '@framework/api'

const config = getConfig()

const product = await getProduct({
  variables: { slug },
  config,
})

getAllProducts

import getAllProducts from '@framework/product/get-all-products'
import { getConfig } from '@framework/api'

const config = getConfig()

const { products } = await getAllProducts({
  variables: { first: 12 },
  config,
})

getAllCollections

import getAllCollections from '@framework/product/get-all-collections'
import { getConfig } from '@framework/api'

const config = getConfig()

const collections = await getAllCollections({
  config,
})

getAllPages

import getAllPages from '@framework/common/get-all-pages'
import { getConfig } from '@framework/api'

const config = getConfig()

const pages = await getAllPages({
  variables: { first: 12 },
  config,
})

Code generation

This provider makes use of GraphQL code generation. The schema.graphql and schema.d.ts files contain the generated types & schema introspection results.

When developing the provider, changes to any GraphQL operations should be followed by re-generation of the types and schema files:

From the project root dir, run:

yarn generate:shopify
```

```md
Commerce Framework

    Commerce Framework
        Commerce Hooks
            CommerceProvider
        Authentication Hooks
            useSignup
            useLogin
            useLogout
        Customer Hooks
            useCustomer
        Product Hooks
            usePrice
            useSearch
        Cart Hooks
            useCart
            useAddItem
            useUpdateItem
            useRemoveItem
        Wishlist Hooks
        Commerce API
        More

The commerce framework ships multiple hooks and a Node.js API, both using an underlying headless e-commerce platform, which we call commerce providers.

The core features are:

    Code splitted hooks for data fetching using SWR, and to handle common user actions
    A Node.js API for initial data population, static generation of content and for creating the API endpoints that connect to the hooks, if required.

    👩‍🔬 If you would like to contribute a new provider, check the docs for Adding a new Commerce Provider.

    🚧 The core commerce framework is under active development, new features and updates will be continuously added over time. Breaking changes are expected while we finish the API.

Commerce Hooks

A commerce hook is a React hook that's connected to a commerce provider. They focus on user actions and data fetching of data that wasn't statically generated.

Data fetching hooks use SWR underneath and you're welcome to use any of its return values and options. For example, using the useCustomer hook:

const { data, isLoading, error } = useCustomer({
  swrOptions: {
    revalidateOnFocus: true,
  },
})

CommerceProvider

This component adds the provider config and handlers to the context of your React tree for it's children. You can optionally pass the locale to it:

import { CommerceProvider } from '@framework'

const App = ({ locale = 'en-US', children }) => {
  return <CommerceProvider locale={locale}>{children}</CommerceProvider>
}

Authentication Hooks
useSignup

Returns a signup function that can be used to sign up the current visitor:

import useSignup from '@framework/auth/use-signup'

const SignupView = () => {
  const signup = useSignup()

  const handleSignup = async () => {
    await signup({
      email,
      firstName,
      lastName,
      password,
    })
  }

  return <form onSubmit={handleSignup}>{children}</form>
}

useLogin

Returns a login function that can be used to sign in the current visitor into an existing customer:

import useLogin from '@framework/auth/use-login'

const LoginView = () => {
  const login = useLogin()
  const handleLogin = async () => {
    await login({
      email,
      password,
    })
  }

  return <form onSubmit={handleLogin}>{children}</form>
}

useLogout

Returns a logout function that signs out the current customer when called.

import useLogout from '@framework/auth/use-logout'

const LogoutButton = () => {
  const logout = useLogout()
  return (
    <button type="button" onClick={() => logout()}>
      Logout
    </button>
  )
}

Customer Hooks
useCustomer

Fetches and returns the data of the signed in customer:

import useCustomer from '@framework/customer/use-customer'

const Profile = () => {
  const { data, isLoading, error } = useCustomer()

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>{error.message}</p>
  if (!data) return null

  return <div>Hello, {data.firstName}</div>
}

Product Hooks
usePrice

Helper hook to format price according to the commerce locale and currency code. It also handles discounts:

import useCart from '@framework/cart/use-cart'
import usePrice from '@framework/product/use-price'

// ...
const { data } = useCart()
const { price, discount, basePrice } = usePrice(
  data && {
    amount: data.subtotalPrice,
    currencyCode: data.currency.code,
    // If `baseAmount` is used, a discount will be calculated
    // baseAmount: number,
  }
)
// ...

useSearch

Fetches and returns the products that match a set of filters:

import useSearch from '@framework/product/use-search'

const SearchPage = ({ searchString, category, brand, sortStr }) => {
  const { data } = useSearch({
    search: searchString || '',
    categoryId: category?.entityId,
    brandId: brand?.entityId,
    sort: sortStr,
  })

  return (
    <Grid layout="normal">
      {data.products.map((product) => (
        <ProductCard key={product.path} product={product} />
      ))}
    </Grid>
  )
}

Cart Hooks
useCart

Fetches and returns the data of the current cart:

import useCart from '@framework/cart/use-cart'

const CartTotal = () => {
  const { data, isLoading, isEmpty, error } = useCart()

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>{error.message}</p>
  if (isEmpty) return <p>The cart is empty</p>

  return <p>The cart total is {data.totalPrice}</p>
}

useAddItem

Returns a function that adds a new item to the cart when called, if this is the first item it will create the cart:

import { useAddItem } from '@framework/cart'

const AddToCartButton = ({ productId, variantId }) => {
  const addItem = useAddItem()

  const addToCart = async () => {
    await addItem({
      productId,
      variantId,
    })
  }

  return <button onClick={addToCart}>Add To Cart</button>
}

useUpdateItem

Returns a function that updates a current item in the cart when called, usually the quantity.

import { useUpdateItem } from '@framework/cart'

const CartItemQuantity = ({ item }) => {
  const [quantity, setQuantity] = useState(item.quantity)
  const updateItem = useUpdateItem({ item })

  const updateQuantity = async (e) => {
    const val = e.target.value

    setQuantity(val)
    await updateItem({ quantity: val })
  }

  return (
    <input
      type="number"
      max={99}
      min={0}
      value={quantity}
      onChange={updateQuantity}
    />
  )
}

If the quantity is lower than 1 the item will be removed from the cart.
useRemoveItem

Returns a function that removes an item in the cart when called:

import { useRemoveItem } from '@framework/cart'

const RemoveButton = ({ item }) => {
  const removeItem = useRemoveItem()
  const handleRemove = async () => {
    await removeItem(item)
  }

  return <button onClick={handleRemove}>Remove</button>
}

Wishlist Hooks

Wishlist hooks work just like cart hooks. Feel free to check how those work first.

The example below shows how to use the useWishlist, useAddItem and useRemoveItem hooks:

import { useWishlist, useAddItem, useRemoveItem } from '@framework/wishlist'

const WishlistButton = ({ productId, variant }) => {
  const addItem = useAddItem()
  const removeItem = useRemoveItem()
  const { data, isLoading, isEmpty, error } = useWishlist()

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>{error.message}</p>
  if (isEmpty) return <p>The wihslist is empty</p>

  const { data: customer } = useCustomer()
  const itemInWishlist = data?.items?.find(
    (item) => item.product_id === productId && item.variant_id === variant.id
  )

  const handleWishlistChange = async (e) => {
    e.preventDefault()
    if (!customer) return

    if (itemInWishlist) {
      await removeItem({ id: itemInWishlist.id })
    } else {
      await addItem({
        productId,
        variantId: variant.id,
      })
    }
  }

  return (
    <button onClick={handleWishlistChange}>
      <Heart fill={itemInWishlist ? 'var(--pink)' : 'none'} />
    </button>
  )
}

Commerce API

While commerce hooks focus on client side data fetching and interactions, the commerce API focuses on static content generation for pages and API endpoints in a Node.js context.

    The commerce API is currently going through a refactor in #252 - We'll update the docs once the API is released.

More
Feel free to read through the source for more usage, and check the commerce vercel demo and commerce repo for usage examples: (demo.vercel.store) (repo)
```
```
For a seamless integration of Vercel, Next.js, and
Shopify, the fastest and most reliable method is to use the official Next.js Commerce starter kit. It provides a complete, optimized storefront template that you can clone and deploy directly to Vercel, which will automatically configure the Shopify integration for you. 
Here is a step-by-step guide for a seamless integration.
Step 1: Set up your Shopify store

    Create a Shopify partner account: If you don't have one, create a Shopify Partner account. This is free and allows you to create unlimited development stores for testing.
    Create a development store: From your Partner dashboard, create a development store to build and test your headless setup.
    Install the Headless sales channel: In your store's admin, go to Settings > Apps and sales channels, click "Shopify App Store," search for and install the Headless app.
    Create a new storefront: In the Headless app, click Create storefront. You'll receive a public access token. Copy this token and save it, as you'll need it for your Next.js application. 

Step 2: Deploy the Next.js Commerce template to Vercel

    Visit the template: Go to vercel.com/templates/next.js/nextjs-commerce and click the Clone & Deploy button.
    Connect your Git account: Authorize Vercel to create a new repository in your GitHub, GitLab, or Bitbucket account. This repository will contain your storefront's code.
    Integrate Shopify: During the deployment process, Vercel will prompt you to add an integration. Choose Shopify and follow the on-screen instructions. Vercel automatically sets the necessary environment variables (COMMERCE_PROVIDER, NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN, and NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN).
    Deploy: Click Deploy. Vercel will build and deploy your headless storefront, making it live on a Vercel URL. 

Step 3: Configure the Shopify Headless theme
To ensure a smooth transition from your Next.js storefront to Shopify's checkout, you need to configure a special theme.

    Download the theme: Get the latest version of the official Shopify Headless theme by downloading the zip file from the Instant Commerce GitHub repository.
    Upload the theme to Shopify: In your Shopify admin, go to Online Store > Themes, click Add theme, and select Upload zip file. Choose the file you just downloaded.
    Publish the theme: After uploading, publish the theme to make it active for your store.
    Configure theme settings: Customize the new Headless theme to enter your Vercel URL, ensuring that the checkout and order status pages will redirect users back to the correct headless domain. 

Step 4: Develop and customize locally

    Clone the repository: Once the project is deployed, clone the newly created Git repository to your local machine.
    Pull environment variables: Install the Vercel CLI by running npm install -g vercel. Then, run vercel env pull to download your secure environment variables into a local .env file.
    Run locally: Use npm run dev to start the Next.js development server. Your storefront will be running locally, connected to your Shopify store.
    Start customizing: With the local setup complete, you can begin customizing the storefront's UI, adding new components, and modifying the design using the Next.js Commerce codebase. 

Step 5: Handle webhooks for real-time data
To keep your headless storefront in sync with changes in Shopify (e.g., product updates), you need to set up webhooks for instant data revalidation.

    Create a secure webhook secret: In your Vercel project, go to Settings > Environment Variables and add a secret variable for your webhooks, such as SHOPIFY_REVALIDATION_SECRET.
    Add the webhook in Shopify: In your Shopify Admin, navigate to the Headless app and configure webhooks to notify your Next.js application of data changes. Provide your Vercel deployment URL and the webhook secret for secure revalidation. 
```

generate a prompt

### Assistant:
<details type="reasoning" done="true" duration="3" view="" last_tool_call_name="">
<summary>Thought for 3 seconds</summary>
> We are generating a prompt for an AI assistant to help with integrating Shopify with Next.js and Vercel. The prompt should capture all the steps and details provided in the user's input.
> 
> The user has provided:
> 1. Information about the Shopify Provider for a commerce framework.
> 2. Details about the commerce hooks and APIs.
> 3. A step-by-step guide for integrating Shopify with Next.js and Vercel.
> 
> We need to combine these into a coherent prompt that asks the AI to act as a developer assistant for setting up this integration.
> 
> The prompt should include:
> - The goal: seamless integration of Shopify, Next.js, and Vercel.
> - Step-by-step instructions from the user.
> - Any additional context from the provided documentation (like the Shopify Provider details).
> 
> We'll structure the prompt to be clear and actionable, so the AI can provide guidance at each step.
> 
> Let's draft the prompt:
</details>
# Integration Guide: Shopify + Next.js + Vercel

I'm building a headless e-commerce storefront using **Next.js**, **Vercel**, and **Shopify**. I need a comprehensive implementation plan covering:

## Core Requirements
1. **Shopify Setup**: Development store, Headless sales channel, storefront creation
2. **Vercel Deployment**: Using Next.js Commerce template with automatic Shopify integration
3. **Theme Configuration**: Setting up Shopify Headless theme for checkout flow
4. **Local Development**: Cloning repo, environment setup, and customization
5. **Webhook Management**: Real-time data synchronization between Shopify and Next.js

## Technical Stack Details
- **Commerce Framework**: Using `@framework` package with Shopify provider
- **Key Hooks Needed**: `useCart`, `useAddItem`, `useCustomer`, etc.
- **GraphQL Operations**: Product queries, cart mutations via Shopify Storefront API
- **Environment Variables**: `NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN`, `NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN`

## Specific Implementation Questions
1. How to properly configure the `.env.local` file with Shopify credentials?
2. What's the best approach for handling cart state across sessions?
3. How to implement wishlist functionality with Shopify?
4. What webhook events should I subscribe to for optimal performance?
5. How to customize the Shopify Headless theme for my brand?

Provide a step-by-step checklist with code snippets where appropriate, focusing on:
- Environment configuration
- Hook implementations for core e-commerce flows
- Theme customization best practices
- Performance optimization techniques
- Error handling strategies

Include references to relevant documentation sections from the provided materials.

### User:
homedepot products scrapping server side

### Assistant:
<details type="reasoning" done="true" duration="22" view="" last_tool_call_name="">
<summary>Thought for 22 seconds</summary>
> We are going to scrape Home Depot products server-side. Since Home Depot doesn't provide an official API for scraping, we'll need to use web scraping techniques. However, note that scraping websites may violate their terms of service, so proceed with caution and consider using official APIs if available.
> 
> Given the constraints, we'll outline a server-side solution using Node.js and a library like Puppeteer or Cheerio. We'll focus on extracting product details such as name, price, image, description, etc.
> 
> Steps:
> 1. Set up a Node.js project.
> 2. Install necessary dependencies (Puppeteer, Cheerio, etc.).
> 3. Write a script to fetch and parse Home Depot product pages.
> 4. Handle pagination if needed.
> 5. Store or process the scraped data.
> 
> However, note that Home Depot has anti-scraping measures. We might need to:
> - Use headers to mimic a browser.
> - Rotate user agents.
> - Use proxies if necessary.
> - Implement delays between requests.
> 
> Let's write a basic example using Puppeteer to scrape a single product page. Then, we can extend it to multiple products.
> 
> But note: The user asked for server-side scraping. We can run this as a cron job or an API endpoint.
> 
> Since the user mentioned "server side", we assume they want to run this on a server (like Vercel, Netlify, or a dedicated server).
> 
> However, note that Vercel and similar platforms have restrictions on running headless browsers due to resource limitations. So, if deploying to Vercel, we might need to use a serverless function that uses a lightweight scraper or offload the scraping to a dedicated server.
> 
> Alternatively, we can use a service like Apify or ScrapingBee that provides cloud-based scrapers.
> 
> But let's stick to a basic Node.js script for demonstration.
> 
> Example structure:
> 
> ```javascript
> const puppeteer = require('puppeteer');
> 
> async function scrapeHomeDepotProduct(url) {
>   const browser = await puppeteer.launch();
>   const page = await browser.newPage();
> 
>   // Set user agent to mimic a browser
>   await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
> 
>   try {
>     await page.goto(url, { waitUntil: 'networkidle2' });
> 
>     // Extract product details
>     const product = await page.evaluate(() => {
>       // Example selectors (these might change, so inspect the actual page)
>       const title = document.querySelector('.product-title')?.innerText;
>       const price = document.querySelector('.price')?.innerText;
>       const imageUrl = document.querySelector('.primary-image')?.src;
> 
>       return { title, price, imageUrl };
>     });
> 
>     console.log(product);
>   } catch (error) {
>     console.error('Error:', error);
>   } finally {
>     await browser.close();
>   }
> }
> 
> scrapeHomeDepotProduct('https://www.homedepot.com/p/some-product-id');
> ```
> 
> But note: Home Depot's HTML structure might change, so the selectors above are just placeholders. You must inspect the actual page to get the correct selectors.
> 
> Also, for multiple products, we would need to:
> 1. Find a way to get product URLs (maybe from a sitemap, category pages, or search results).
> 2. Loop through each URL and scrape.
> 
> However, scraping entire sites is complex and might not be feasible without proper infrastructure.
> 
> Alternative approach: Use Home Depot's official API if available. But as of now, Home Depot does not offer a public API for scraping.
> 
> Another alternative: Use a third-party service that aggregates product data, but that might not be cost-effective.
> 
> Given the complexity and potential legal issues, it's important to note that scraping should only be done for personal projects and with respect to the website's robots.txt and terms of service.
> 
> If the goal is to integrate Home Depot products into an e-commerce site, consider using affiliate programs or official partnerships if available.
> 
> But since the user specifically asked for scraping, we'll proceed with the technical solution.
> 
> For server-side execution, we can wrap this in a serverless function (like AWS Lambda, Vercel Functions, etc.) but note the limitations of headless browsers in serverless environments.
> 
> Alternatively, we can pre-render the data during build time (if using Next.js) but that might not be suitable for dynamic data.
> 
> Given the constraints, here's a more robust example that handles pagination and multiple products:
> 
> ```javascript
> const puppeteer = require('puppeteer');
> 
> async function scrapeHomeDepotCategory(categoryUrl) {
>   const browser = await puppeteer.launch();
>   const page = await browser.newPage();
>   await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
> 
>   try {
>     await page.goto(categoryUrl, { waitUntil: 'networkidle2' });
> 
>     // Scroll down to load more products (if infinite scroll)
>     await autoScroll(page);
> 
>     // Extract product links
>     const productLinks = await page.$$eval('.product-link', links => 
>       links.map(link => link.href).filter(href => href.startsWith('https://www.homedepot.com'))
>     );
> 
>     const products = [];
>     for (let i = 0; i < productLinks.length; i++) {
>       const productUrl = productLinks[i];
>       const product = await scrapeSingleProduct(page, productUrl);
>       products.push(product);
>     }
> 
>     console.log(products);
>   } catch (error) {
>     console.error('Error:', error);
>   } finally {
>     await browser.close();
>   }
> }
> 
> async function scrapeSingleProduct(page, url) {
>   // Navigate to the product page
>   await page.goto(url, { waitUntil: 'networkidle2' });
> 
>   // Extract product details
>   const product = await page.evaluate(() => {
>     // Adjust these selectors based on the actual page
>     const title = document.querySelector('.product-title').innerText;
>     const price = document.querySelector('.price').innerText;
>     const imageUrl = document.querySelector('.primary-image').src;
>     const description = document.querySelector('.description').innerText;
> 
>     return { title, price, imageUrl, description };
>   });
> 
>   return product;
> }
> 
> async function autoScroll(page){
>   await page.evaluate(async () => {
>     await new Promise((resolve) => {
>       let totalHeight = 0;
>       const distance = 100;
>       const timer = setInterval(() => {
>         const scrollHeight = document.body.scrollHeight;
>         window.scrollBy(0, distance);
>         totalHeight += distance;
> 
>         if(totalHeight >= scrollHeight){
>           clearInterval(timer);
>           resolve();
>         }
>       }, 100);
>     });
>   });
> }
> 
> scrapeHomeDepotCategory('https://www.homedepot.com/b/near-me/N-5yc1vZb9jg');
> ```
> 
> Note: This is a simplified example. In reality, you would need to handle:
> - Dynamic content loading (using `page.waitForSelector`)
> - Captchas or other anti-bot measures
> - Rate limiting and retries
> - Data storage (database or file)
> 
> Also, remember to check Home Depot's `robots.txt` file at `https://www.homedepot.com/robots.txt` to see what is allowed to be scraped.
> 
> Given the complexity and potential legal issues, it's often better to look for official APIs or data feeds if available.
> 
> If you decide to proceed with scraping, monitor the website for changes and adjust your selectors accordingly.
> 
> Finally, note that this example is for educational purposes only. Always comply with the website's terms of service and copyright laws.
</details>
# Home Depot Product Scraping Server-Side Solution

I'll help you build a server-side solution to scrape Home Depot product data. Here's a comprehensive implementation plan:

## Approach Overview
1. Use Puppeteer for headless browser automation
2. Implement rate limiting and proxy rotation
3. Handle dynamic content loading
4. Structure data extraction with reusable functions
5. Store results in a database or export format

## Implementation Steps

### 1. Project Setup
```bash
mkdir home-depot-scraper
cd home-depot-scraper
npm init -y
npm install puppeteer cheerio axios dotenv
```

### 2. Basic Scraper Structure
```javascript
require('dotenv').config();
const puppeteer = require('puppeteer');
const fs = require('fs');

// Configuration
const CONFIG = {
  BASE_URL: 'https://www.homedepot.com',
  CATEGORIES: ['p/plumbing/90337', 'p/electrical/204767145'],
  MAX_PAGES: 5,
  DELAY_BETWEEN_REQUESTS: 3000,
};

// Main scraping function
async function scrapeHomeDepot() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    for (const category of CONFIG.CATEGORIES) {
      await scrapeCategory(browser, `${CONFIG.BASE_URL}/${category}`);
    }
  } catch (error) {
    console.error('Scraping failed:', error);
  } finally {
    await browser.close();
  }
}

// Category scraping logic
async function scrapeCategory(browser, url) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    // Handle pagination
    for (let i = 0; i < CONFIG.MAX_PAGES; i++) {
      await extractProducts(page);
      
      // Check for next page
      const nextPageBtn = await page.$('a.pagination__btn--next');
      if (!nextPageBtn) break;
      
      await page.click('a.pagination__btn--next');
      await page.waitForTimeout(CONFIG.DELAY_BETWEEN_REQUESTS);
    }
  } finally {
    await page.close();
  }
}

// Product extraction function
async function extractProducts(page) {
  const products = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.product-item'))
      .map(item => ({
        title: item.querySelector('.product-title').textContent.trim(),
        price: item.querySelector('.price').textContent.trim(),
        sku: item.querySelector('.sku').textContent.trim(),
        imageUrl: item.querySelector('img.product-image').src,
        rating: item.querySelector('.stars-rating').getAttribute('aria-label'),
        reviews: item.querySelector('.reviews-count').textContent.trim()
      }));
  });
  
  // Save to JSON file
  fs.appendFileSync('products.json', JSON.stringify(products, null, 2));
}

// Start scraping
scrapeHomeDepot();
```

### 3. Advanced Features to Add

#### Proxy Rotation
```javascript
const PROXIES = [
  'http://proxy1.example.com:8080',
  'http://proxy2.example.com:8080',
  // Add more proxies
];

function getRandomProxy() {
  return PROXIES[Math.floor(Math.random() * PROXIES.length)];
}

// Modify launch config
const browser = await puppeteer.launch({
  headless: true,
  args: [`--proxy-server=${getRandomProxy()}`]
});
```

#### User-Agent Rotation
```javascript
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
  // Add more user agents
];

await page.setUserAgent(USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)]);
```

#### CAPTCHA Handling
```javascript
// Detect CAPTCHA
const captchaDetected = await page.evaluate(() => {
  return document.querySelector('#captcha-container') !== null;
});

if (captchaDetected) {
  // Implement CAPTCHA solving service integration
  await solveCaptcha(page);
}
```

### 4. Data Storage Options
```javascript
// Option 1: MongoDB
const MongoClient = require('mongodb').MongoClient;
const uri = process.env.MONGODB_URI;

async function saveToDatabase(products) {
  const client = new MongoClient(uri);
  await client.connect();
  const collection = client.db("homeDepot").collection("products");
  await collection.insertMany(products);
  await client.close();
}

// Option 2: PostgreSQL
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.POSTGRES_URL,
});

async function saveToPostgres(products) {
  const query = `
    INSERT INTO products (title, price, sku, image_url, rating, reviews)
    VALUES ($1, $2, $3, $4, $5, $6)
  `;
  
  for (const product of products) {
    await pool.query(query, [
      product.title,
      product.price,
      product.sku,
      product.imageUrl,
      product.rating,
      product.reviews
    ]);
  }
}
```

### 5. Deployment Considerations
- Use Docker containerization for consistent environments
- Schedule with cron jobs or serverless functions (AWS Lambda/Azure Functions)
- Monitor with logging services (Sentry, Loggly)
- Implement retry mechanisms for failed requests

### 6. Legal and Ethical Considerations
1. Review Home Depot's `robots.txt`: `https://www.homedepot.com/robots.txt`
2. Respect crawl-delay directives
3. Avoid excessive request rates
4. Cache results to minimize repeated requests
5. Consider official APIs or affiliate programs instead of scraping

### 7. Alternative Approaches
1. **Official APIs**: Check if Home Depot offers product data feeds
2. **Affiliate Programs**: Join Home Depot's affiliate network for structured data
3. **Third-party Services**: Use aggregators like Jungle Scout or SEMrush
4. **Headless CMS**: Consider Contentful or Sanity for managed product data

Would you like me to elaborate on any specific aspect of this implementation?

