# test_transform.py
import json
import asyncio
from optimus_v3 import OptimusV3

async def main():
    """
    Test script to run the OptimusV3 transformation pipeline on a sample product.
    """
    # Initialize the OptimusV3 engine
    p = OptimusV3()

    # Load a sample product from a JSON file
    try:
        with open("sample_product.json", "r", encoding="utf-8") as f:
            prod = json.load(f)
    except FileNotFoundError:
        print("[ERROR] sample_product.json not found. Please create it in the same directory.")
        return
    except json.JSONDecodeError:
        print("[ERROR] sample_product.json is not a valid JSON file.")
        return

    # Run the full transformation pipeline, including embeddings
    print("--- Starting Product Transformation ---")
    transformed_data = await p.transform_product(prod, include_embeddings=True)
    print("--- Transformation Complete ---\
")

    # Print the final result in a readable format
    print("--- OptimusV3 Output ---")
    # transform_product now returns a dictionary, so no .dict() call is needed
    print(json.dumps(transformed_data, indent=2, ensure_ascii=False))

    # Optional: Save the result to Supabase
    # Uncomment the following lines to save the result to your database
    # 
    # if prod.get("id"):
    #     print("\n--- Saving to Supabase ---")
    #     success = await p.process_and_sync_product(prod, include_embeddings=True) # Call the full sync method
    #     if success:
    #         print("✅ Successfully saved to Supabase.")
    #     else:
    #         print("❌ Failed to save to Supabase.")
    # else:
    #     print("\n--- Skipping Supabase Save ---")
    #     print("Product has no 'id' field. Cannot save to database.")

if __name__ == "__main__":
    asyncio.run(main())
