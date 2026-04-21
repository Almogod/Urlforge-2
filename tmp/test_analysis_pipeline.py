import asyncio
import sys
import os

# Add src to path if needed (depending on where this is run)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.data_processing_service import process_site_homepage
from src.services.site_analysis_service import synthesize_business_analysis
from src.utils.logger import logger

async def main():
    if len(sys.argv) < 2:
        print("Usage: python tmp/test_analysis_pipeline.py <url>")
        return

    url = sys.argv[1]
    logger.info(f"--- Starting Pipeline Test for {url} ---")
    
    # 1. Scrape, Clean, Chunk, and Structure
    processed_data = await process_site_homepage(url)
    
    if "error" in processed_data:
        logger.error(f"Pipeline failed at processing stage: {processed_data['error']}")
        return

    logger.info(f"Processing complete. Structured data for {len(processed_data['structured_data'])} chunks.")
    
    # 2. Final Synthesis
    final_report = synthesize_business_analysis(url, processed_data['structured_data'])
    
    # 3. Output results
    output_file = "site_analysis_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    logger.info(f"--- Pipeline Test Complete ---")
    logger.info(f"Final report saved to {output_file}")
    
    print("\n" + "="*50)
    print("FINAL BUSINESS ANALYSIS PREVIEW")
    print("="*50)
    print(final_report[:500] + "...")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
