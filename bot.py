import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

def main():
    st.title("WebHelpers Chatbot")
    st.write("Enter the URL of the product page:")
    
    webpage_url = st.text_input("URL")
    
    if st.button("Scrape Data"):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            session = requests.Session()
            time.sleep(2)
            response = session.get(webpage_url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get title
                try:
                    title = soup.find("span", attrs={"id": 'productTitle'})
                    title_value = title.text
                    title_string = title_value.strip()
                    if title_string == "Title not available":
                        title_string = None
                except Exception:
                    title_string = None

                # Get price
                try:
                    price_whole = soup.find("span", class_='a-price-whole').text.strip()
                    price_fractional = soup.find("span", class_='a-price-fraction').text.strip()
                    price_currency = soup.find("span", class_='a-price-symbol').text.strip()
                    price = f"{price_currency}{price_whole}.{price_fractional}"
                except Exception:
                    price = "Price not available"

                # Get rating
                try:
                    rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
                except Exception:
                    try:
                        rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
                    except:
                        rating = "Rating not available"

                # Get availability
                try:
                    available = soup.find("div", attrs={'id': 'availability'})
                    available = available.find("span").string.strip()
                except Exception:
                    available = "Availability not available"

                if title_string:
                    scraped_data = {
                        'title': title_string,
                        'price': price,
                        'rating': rating,
                        'availability': available,
                    }
                    
                    st.success("Data successfully scraped!")
                    st.header("Scraped Product Data")
                    st.write(scraped_data)
                    
                    st.subheader("Chat with WebHelpers - Your Shopping Assistant")
                    user_input = st.text_area("You:")
                    chat_history = []

                    if st.button("Send"):
                        user_input = user_input.lower()
                        chat_history.append(f"You: {user_input}")
                        found_match = False

                        for key in scraped_data.keys():
                            if key in user_input:
                                value = scraped_data.get(key, "Not available.")
                                response = f"The {key} of the product is: {value}"
                                chat_history.append(response)
                                found_match = True

                        if not found_match:
                            chat_history.append("I'm sorry, I didn't understand your question. Could you please rephrase it?")

                        st.text_area("Chat History", value="\n".join(chat_history), height=200)
                        
                else:
                    st.error("Product title is not available.")
            else:
                st.error(f"Failed to retrieve the Amazon page: {webpage_url}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
if __name__ == "__main__":
    main()
