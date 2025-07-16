import streamlit as st
import requests
import logging
import json

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    """
    Fetch data from the API with robust error handling.
    Returns None if the request fails, with user-friendly error messages.
    """
    try:
        logger.info("Attempting to fetch data from API")
        response = requests.get("YOUR_API_URL", timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        # Cache the data locally as a fallback
        with open("backup_data.json", "w") as f:
            json.dump(data, f)
        return data
    except requests.exceptions.ConnectionError as e:
        st.error(f"Failed to connect to the API: {str(e)}. Please check your network or API availability.")
        logger.error(f"Connection error: {str(e)}")
        return load_fallback_data()
    except requests.exceptions.HTTPError as e:
        st.error(f"API returned an error: {str(e)}")
        logger.error(f"HTTP error: {str(e)}")
        return load_fallback_data()
    except requests.exceptions.Timeout as e:
        st.error(f"Request timed out: {str(e)}. Please try again later.")
        logger.error(f"Timeout error: {str(e)}")
        return load_fallback_data()
    except requests.exceptions.RequestException as e:
        st.error(f"An unexpected error occurred while fetching data: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return load_fallback_data()

def load_fallback_data():
    """
    Load cached data as a fallback if the API request fails.
    Returns None if no cached data is available.
    """
    try:
        with open("backup_data.json", "r") as f:
            st.warning("Using cached data due to API failure.")
            return json.load(f)
    except FileNotFoundError:
        st.error("No cached data available.")
        logger.warning("No cached data found.")
        return None

def main():
    st.title("Arbovirose Data Dashboard")
    
    # Slider for selecting period
    periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
    
    # Load data
    data = load_data()
    
    if data is not None:
        # Display data (example: assuming data is a list of records)
        st.write(f"Data for the last {periodo} days:")
        st.json(data)  # Replace with actual data visualization as needed
    else:
        st.error("Unable to display data due to an error.")

if __name__ == "__main__":
    main()
