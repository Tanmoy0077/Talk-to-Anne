import fitz  # PyMuPDF
import re
import csv
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
import time
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
date_pattern = re.compile(
    r"\b(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)\s*,\s*(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{1,2}\s*,\s*\d{4}\b",
    flags=re.IGNORECASE
)

# Step 1: Extract raw text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# Step 2: Chunking using dates from entries  
def split_by_dates(text):
    diary_end_marker = "ANNE'S DIARY ENDS HERE."
    diary_end_index = text.find(diary_end_marker)

    if diary_end_index != -1:
        diary_text = text[:diary_end_index]
        afterword_text = text[diary_end_index:].strip()
    else:
        diary_text = text
        afterword_text = ""

    matches = list(date_pattern.finditer(diary_text))
    chunks = []

    if matches:
        # Foreword
        first_start = matches[0].start()
        chunks.append(("Foreword", diary_text[:first_start].strip()))

        # Diary Entries
        for i in range(len(matches)):
            start = matches[i].start()

            # If not last entry
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                # Last entry should end at diary_end_index (if available)
                end = diary_end_index if diary_end_index != -1 else len(text)

            date_str = matches[i].group()
            content = text[start:end].strip()
            chunks.append((date_str, content))

    else:
        chunks.append(("Full Text", diary_text.strip()))

    # Append Afterword if present
    if afterword_text:
        chunks.append(("Afterword", afterword_text))

    return chunks

# Step 3: Saving Chunks to csv
def save_chunks_to_csv(chunks, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['chunk_title', 'chunk_text'])
        writer.writeheader()
        for title, text in chunks:
            writer.writerow({'chunk_title': title, 'chunk_text': text})

# Step 4: LLM Call for description and people generation
def generate_chunk_summary_prompt(chunk_text):
  parser = JsonOutputParser()

  prompt = PromptTemplate(
    input_variables=["chunk_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    template="""
      You are analyzing a diary entry. Extract the key information.

      Please return a JSON object with the following structure:

      {{
        "description": "<short summary containing the important points in the text>",
        "people_involved": ["<list of people mentioned in the text>"]
      }}

      {format_instructions}

      Text to analyze:
      \"\"\"
      {chunk_text}
      \"\"\"
      """

  )


  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.2, api_key=api_key)


  chain = prompt | llm | parser
  response = chain.invoke({"chunk_text": chunk_text})

  return response


# def test_llm_on_sample_chunks(chunks):
#     for i, (title, text) in enumerate(chunks):
#         print(f"\n=== Chunk {i+1}: {title} ===")
#         try:
#             result = generate_chunk_summary_prompt(text)
#             print("Description:", result.get("description", ""))
#             print("People Involved:", result.get("people_involved", []))
#         except Exception as e:
#             print(f"❌ Error in chunk {title}:", e)


# Step 5: Saving chunks along with their descriptions in a CSV
def save_chunks_with_summary_to_csv(chunks, output_csv="../../documents/diary_summary_output.csv"):
    with open(output_csv, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['chunk_title', 'chunk_text', 'description', 'people_involved'])
        writer.writeheader()

        batch_size = 10
        total_chunks = len(chunks)

        for i in tqdm(range(0, total_chunks, batch_size), desc="Processing chunks in batches"):
            batch = chunks[i:i+batch_size]

            for chunk_title, chunk_text in batch:
                try:
                    result = generate_chunk_summary_prompt(chunk_text)

                    writer.writerow({
                        'chunk_title': chunk_title,
                        'chunk_text': chunk_text,
                        'description': result.get("description", ""),
                        'people_involved': ', '.join(result.get("people_involved", []))
                    })

                except Exception as e:
                    print(f"Error processing chunk '{chunk_title}':", e)
                    writer.writerow({
                        'chunk_title': chunk_title,
                        'chunk_text': chunk_text,
                        'description': '',
                        'people_involved': ''
                    })

            # Wait 60 seconds after each batch
            if i + batch_size < total_chunks:
                print("⏳ Waiting 60 seconds to respect Gemini rate limits...")
                time.sleep(60)



if __name__ == "__main__":
    pdf_path = "../../documents/Anne-Frank-The-Diary-Of-A-Young-Girl.pdf"
    # print(pdf_path)

    raw_text = extract_text_from_pdf(pdf_path)
    # print(raw_text)

    chunks = split_by_dates(raw_text)
    # Preview the chunks
    # for i, (title, content) in enumerate(chunks):
    #     print(f"\n--- Chunk {i+1}: {title} ---\n")
    #     print(content)

    save_chunks_to_csv(chunks, filename="../../documents/anne_frank_diary_chunks.csv")
    # df=pd.read_csv("anne_frank_diary_chunks.csv")
    # print(df)
    # print(chunks)

    # print(test_llm_on_sample_chunks(chunks[:3]))
    save_chunks_with_summary_to_csv(chunks)
    # df_sum= pd.read_csv("diary_summary_output.csv")
    # print(df_sum)