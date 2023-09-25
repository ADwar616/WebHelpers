import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

try:
    import SessionState
except ModuleNotFoundError:
    # Create a new module named SessionState
    code = '''import streamlit.ReportThread as ReportThread
from streamlit.server.Server import Server

class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get(**kwargs):
    ctx = ReportThread.get_report_ctx()
    session = None
    session_id = ctx.session_id
    session_info = Server.get_current()._get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    this_session = session_info.session

    if not hasattr(this_session, "_custom_session_state"):
        this_session._custom_session_state = SessionState(**kwargs)
    return this_session._custom_session_state'''

    with open('SessionState.py', 'w') as file:
        file.write(code)

import SessionState

def main():
    st.title("WebHelpers Chatbot")
    st.write("Enter the URL of the product page:")
    
    webpage_url = st.text_input("URL")
    
    state = SessionState.get(chat_history=[], user_input="")
    
    user_input = st.text_area("You:", value=state.user_input)
    
    if st.button("Send"):
        state.user_input = user_input.lower()
        state.chat_history.append(f"You: {state.user_input}")
        
        # Scrape product data
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
                    
                    found_match = False

                    for key in scraped_data.keys():
                        if key in state.user_input:
                            value = scraped_data.get(key, "Not available.")
                            response = f"The {key} of the product is: {value}"
                            state.chat_history.append(response)
                            found_match = True

                    if not found_match:
                        state.chat_history.append("I'm sorry, I didn't understand your question. Could you please rephrase it?")
                        
                else:
                    st.error("Product title is not available.")
            else:
                st.error(f"Failed to retrieve the Amazon page: {webpage_url}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
        state.user_input=""
        
    st.text_area("Chat History", value="\n".join(state.chat_history), height=200)
            
if __name__ == "__main__":
    main()
