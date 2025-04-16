import sys


from IONPro.Generator.Utils.sources import extract_sources_from_text, recalibrate_source_ids, create_merged_sources, remove_erroneous_sources
from IONPro.Generator.Prompts import format_simple_prompt
from IONPro.Generator.Completions import generate_async_completion
import asyncio

"""
async def retry_source_correction(model_tiers, correction_prompt, fragment1_sources, fragment2_sources):
    sources = None
    if len(model_tiers) == 1:
        raise Exception("Only one model tier provided, no retry")
        return None, None
    else:   
        for tier in model_tiers[1:]:
            print(f"Retrying with {tier}")
            try:
                response = await generate_async_completion(tier, correction_prompt)
                sources = extract_sources_from_text(response)
                sources_dict = create_merged_sources(fragment1_sources, fragment2_sources, sources)
                return response, sources_dict
            except Exception as e:
                continue
    return None, sources
"""

async def correct_source_format(model, response, fragment1_sources, fragment2_sources, unique_id):
    correction_prompt = format_simple_prompt("source_correction", {"text_with_sources": response})
    try:
        response = await generate_async_completion(model, correction_prompt)
        sources = extract_sources_from_text(response)
        sources_dict, erroneous_sources = create_merged_sources(fragment1_sources, fragment2_sources, sources)
        if len(erroneous_sources) > 0:
            print(f"Erroneous sources in source_correction for {unique_id}: {erroneous_sources}")
            response = remove_erroneous_sources(response, erroneous_sources)
    except Exception as e:
        print(f"Error in source_correction for {unique_id}")
        raise e
    
    response, sources_dict = recalibrate_source_ids(response, sources_dict)
    
    return response, sources_dict
