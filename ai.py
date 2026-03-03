import streamlit as st
import requests
from bs4 import BeautifulSoup
import wikipedia
import re

# -------------------------------
# Wikipedia Fetch
# -------------------------------

def get_wikipedia_content(query):
    try:
        page = wikipedia.page(query, auto_suggest=True)
        return page.content
    except:
        try:
            search_results = wikipedia.search(query)
            if search_results:
                page = wikipedia.page(search_results[0])
                return page.content
        except:
            return ""
    return ""

# -------------------------------
# Britannica Fetch
# -------------------------------

def get_britannica_content(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.britannica.com/search?query={query}"
    
    try:
        search_page = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(search_page.text, "html.parser")

        first_result = soup.find("a", class_="result__title")
        if not first_result:
            return ""

        article_url = "https://www.britannica.com" + first_result["href"]
        article_page = requests.get(article_url, headers=headers)
        article_soup = BeautifulSoup(article_page.text, "html.parser")

        paragraphs = article_soup.find_all("p")
        text = " ".join([p.text for p in paragraphs])
        return text
    except:
        return ""

# -------------------------------
# Summarize to ~200 words based on keyword relevance
# -------------------------------

def summarize_text(text, question, max_words=200):
    sentences = re.split(r'(?<=[.!?]) +', text)
    question_words = set(question.lower().split())
    
    # Score sentences by number of question words contained
    scored = []
    for sentence in sentences:
        words = set(sentence.lower().split())
        common_words = words.intersection(question_words)
        score = len(common_words)
        if score > 0:
            scored.append((score, sentence))
    
    # Sort sentences by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    summary_sentences = []
    word_count = 0
    
    for _, sent in scored:
        sent_word_count = len(sent.split())
        if word_count + sent_word_count <= max_words:
            summary_sentences.append(sent)
            word_count += sent_word_count
        else:
            break
    
    # If no sentences matched, fallback to first few sentences
    if not summary_sentences:
        summary_sentences = sentences[:5]

    summary = " ".join(summary_sentences)
    
    # Trim summary to max_words if slightly over
    summary_words = summary.split()
    if len(summary_words) > max_words:
        summary = " ".join(summary_words[:max_words]) + "..."
    
    return summary

# -------------------------------
# Main AI Function
# -------------------------------

def cosmic_tutor(question):
    wiki_text = get_wikipedia_content(question)
    brit_text = get_britannica_content(question)

    combined_text = wiki_text + " " + brit_text

    if not combined_text.strip():
        return "No information found."

    summary = summarize_text(combined_text, question, max_words=200)
    return summary

# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Cosmic Tutor", page_icon="🌌")

st.title("🌌 Cosmic Tutor")
st.write("Ask me anything about astronomy! I will search Wikipedia and Britannica to find an answer and provide a concise summary.")

question = st.text_input("Your question:", "")

if question:
    with st.spinner("Searching for the answer..."):
        answer = cosmic_tutor(question)
    st.markdown("### Answer (up to 200 words):")
    st.write(answer)
