import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk

# Function to extract Product title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.text
        title_string = title_value.strip()
        if title_string == "Title not available":
            return None  # If title is not available, return None
        return title_string
    except Exception:
        return None

# Function to extract Product Prices
def get_price(soup):
    try:
        price_whole = soup.find("span", class_='a-price-whole').text.strip()
        price_fractional = soup.find("span", class_='a-price-fraction').text.strip()
        price_currency = soup.find("span", class_='a-price-symbol').text.strip()
        price = f"{price_currency}{price_whole}.{price_fractional}"
    except Exception:
        price = "Price not available"  # Assign a default value
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
    except Exception:
        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = "Rating not available"  # Assign a default value
    return rating

# Function to extract the number of reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.split()
    except Exception:
        review_count = "Review count not available"  # Assign a default value
    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()
    except Exception:
        available = "Availability not available"  # Assign a default value
    return available

# Function to extract product reviews
def get_reviews(soup):
    reviews = []
    review_elements = soup.find_all("div", class_="a-row a-spacing-small review-data")
    
    for element in review_elements[:10]:  # Extract the first 10 reviews
        review_text = element.find("span", class_="a-size-base review-text").text.strip()
        reviews.append(review_text)
    
    if not reviews:
        reviews = ["No reviews available"]  # Assign a default value if no reviews are found
    
    return reviews

def scrape_single_url(url):
    while True:  # Keep trying until a valid title is obtained
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }

            # Create a session to manage cookies and maintain state
            session = requests.Session()
            time.sleep(2)
            # Use the session for making requests
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = get_title(soup)
                if title:
                    data = {
                        'title': title,
                        'price': get_price(soup),
                        'rating': get_rating(soup),
                        'reviews': get_reviews(soup),
                        'availability': get_availability(soup),
                    }
                    # Print the title once
                    print(f"Product Title: {data['title']}")
                    return data
                else:
                    print("Product title is not available. Retrying...")
            else:
                print(f"Failed to retrieve the Amazon page: {url}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def chat_with_user(scraped_data):
    print("\nWelcome to WebHelpers")
    print("You can ask questions about the product. Type 'exit' to end the conversation.")

    while True:
        user_input = input("\nYou: ").strip().lower()

        if user_input == 'exit':
            print("\nGoodbye!")
            break
        elif user_input == 'proceed':
            print("\nYou can now ask questions about the product.")
        else:
            found_match = False
            for key in scraped_data.keys():
                if key in user_input:
                    value = scraped_data.get(key, "Not available.")
                    print(f"The {key} of the product is: {value}")
                    found_match = True

            if not found_match:
                print("I'm sorry, I didn't understand your question. Could you please rephrase it?")
    
# Streamlit app
def main():
    st.title("WebHelpers Chatbot")
    st.write("Enter the URL of the product page:")
    
    # Get the user's input URL
    webpage_url = st.text_input("URL")
    
    if st.button("Scrape Data"):
        # Scrape product data
        scraped_data = scrape_single_url(webpage_url)

        if scraped_data:
            st.success("Data successfully scraped!")
            
            # Store scraped_data in session state
            st.session_state.scraped_data = scraped_data

            if st.button("Start Chat"):
                # Retrieve scraped_data from session state
                chat_with_user(st.session_state.scraped_data)

if __name__ == "__main__":
    main()
