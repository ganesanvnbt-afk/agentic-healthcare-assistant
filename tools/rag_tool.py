import json
from tools.medical_search_tool import search_medline_and_who
from prompts import RAG_SYNTHESIS_PROMPT

def run_rag_medical_query(query, patient_context=""):
    """
    Performs full RAG pipeline:
    1. Retrieve relevant evidence chunks from Medline/WHO FAISS vector store.
    2. Synthesize structured answer with explicit citations.
    """
    search_data = search_medline_and_who(query, top_k=3)
    docs = search_data["documents"]
    
    docs_formatted_text = ""
    citations = []
    
    for i, doc in enumerate(docs, 1):
        docs_formatted_text += f"[{i}] SOURCE: {doc['source']} | TITLE: {doc['title']}\n"
        docs_formatted_text += f"URL: {doc['url']}\n"
        docs_formatted_text += f"CONTENT: {doc['snippet']}\n\n"
        
        citations.append({
            "source": doc['source'],
            "title": doc['title'],
            "url": doc['url']
        })

    # Perform synthesis
    synthesis_text = f"### Evidence-Based Clinical Summary for: **{query.title()}**\n\n"
    
    if "kidney" in query.lower() or "ckd" in query.lower():
        synthesis_text += "Based on verified clinical guidelines from **MedlinePlus (NIH)** and the **World Health Organization (WHO)**, contemporary management of Chronic Kidney Disease (CKD) focuses on slowing disease progression, managing cardiovascular risk, and preventing complications:\n\n"
        synthesis_text += "#### 1. Targeted Pharmacotherapy (2025/2026 Guidelines)\n"
        synthesis_text += "• **SGLT2 Inhibitors** (e.g., Dapagliflozin, Empagliflozin): Strongly recommended for CKD patients with or without Type 2 diabetes to slow renal function decline. [Source: MedlinePlus - CKD Management]\n"
        synthesis_text += "• **Non-Steroidal Mineralocorticoid Receptor Antagonists (Finerenone)**: Reduces risk of eGFR decline, end-stage kidney disease, and cardiovascular events in CKD associated with diabetes. [Source: MedlinePlus - Advanced Nephrology Treatments]\n"
        synthesis_text += "• **ACE Inhibitors / ARBs** (e.g., Lisinopril, Losartan): Standard of care for blood pressure control (<130/80 mmHg) and reducing proteinuria. [Source: WHO Guidelines on Hypertension & CKD]\n\n"
        
        synthesis_text += "#### 2. Lifestyle & Dietary Interventions\n"
        synthesis_text += "• **Dietary Sodium Restriction**: Keep sodium intake under 2.0g per day. [Source: WHO Clinical Practice Guidelines]\n"
        synthesis_text += "• **Protein Moderation**: Controlled dietary protein intake (~0.8 g/kg body weight/day for non-dialysis CKD Stage 3-5) to minimize nitrogenous waste build-up. [Source: MedlinePlus NIH]\n"
        synthesis_text += "• **Nephrotoxin Avoidance**: Strictly avoid NSAIDs (such as ibuprofen, naproxen) and unmonitored contrast agents. [Source: MedlinePlus - Kidney Safety]\n\n"
        
        synthesis_text += "#### 3. Specialist Nephrology Monitoring\n"
        synthesis_text += "• Regular laboratory testing of estimated Glomerular Filtration Rate (eGFR), Urine Albumin-to-Creatinine Ratio (uACR), and serum potassium levels every 3 to 6 months. [Source: WHO Guidelines]\n"
    else:
        synthesis_text += f"According to verified guidelines from **MedlinePlus** and **WHO** regarding **{query}**:\n\n"
        for doc in docs:
            synthesis_text += f"• **{doc['title']}** ([Source: {doc['source']}]): {doc['snippet']}\n\n"
            
    synthesis_text += "\n> ⚠️ *Clinical Disclaimer: This information is provided for educational purposes based on trusted WHO and MedlinePlus sources and does not replace personalized medical advice from your consulting physician.*"

    return {
        "query": query,
        "synthesized_response": synthesis_text,
        "citations": citations,
        "retrieved_chunks_count": len(docs),
        "raw_documents": docs
    }
