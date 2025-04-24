import requests
import json
import re
from django.conf import settings

class GeminiService:
    # Google Gemini API configuration
    API_KEY = "AIzaSyCNpOf35i0dgiBbU_WRPGAsiJcplZqoZic"
    MODEL_NAME = "gemini-1.5-pro"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    @classmethod
    def generate_response(cls, prompt, max_tokens=1024):
        """
        Generate a response from Google Gemini API
        
        Args:
            prompt (str): The user prompt
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated response
        """
        url = f"{cls.BASE_URL}/{cls.MODEL_NAME}:generateContent?key={cls.API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the generated text from the response
            if "candidates" in result and len(result["candidates"]) > 0:
                if "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"]:
                    parts = result["candidates"][0]["content"]["parts"]
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
            
            return "Unable to generate response"
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return f"Error generating response: {str(e)}"

    @classmethod
    def extract_financial_result(cls, text):
        """
        Attempts to extract a financial calculation result from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Extracted financial result
        """
        # Patterns for common financial results
        patterns = [
            r'₹[\d,]+\.\d{2}',  # ₹1,234.56
            r'₹[\d,]+',         # ₹1,234
            r'INR[\d,]+\.\d{2}',  # INR1,234.56
            r'INR[\d,]+',         # INR1,234
            r'Rs\.[\d,]+\.\d{2}',  # Rs.1,234.56
            r'Rs\.[\d,]+',         # Rs.1,234
            r'[\d,]+\.\d{2}%',   # 12.34%
            r'[\d,]+%',          # 12%
            r'[\d,]+\.\d{2}',    # 1234.56
            r'[\d,]+ years',      # 10 years
            r'[\d,]+ months',     # 10 months
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        # Convert $ to ₹ in results if found
        dollar_patterns = [
            r'\$[\d,]+\.\d{2}',  # $1,234.56
            r'\$[\d,]+'         # $1,234
        ]
        
        for pattern in dollar_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].replace('$', '₹')
        
        # If no clear result pattern, try to find a sentence with 'is' and a number
        sentences = text.split('.')
        for sentence in sentences:
            if ' is ' in sentence.lower() and any(char.isdigit() for char in sentence):
                # Replace $ with ₹ if present
                return sentence.strip().replace('$', '₹')
                
        # Default to first line if nothing else works
        first_line = text.split('\n')[0].strip().replace('$', '₹')
        return first_line if first_line else "Unable to extract result"

    @classmethod
    def generate_financial_advice(cls, user_data):
        """
        Generate personalized financial advice based on user data
        
        Args:
            user_data (dict): User financial data
            
        Returns:
            str: Personalized financial advice
        """
        prompt = f"""
        As a financial advisor, provide personalized advice based on the following user data:
        
        Income: ₹{user_data.get('income', 'N/A')}
        Expenses: ₹{user_data.get('expenses', 'N/A')}
        Savings: ₹{user_data.get('savings', 'N/A')}
        Debt: ₹{user_data.get('debt', 'N/A')}
        
        Please provide 3 actionable financial advice tips that are specific to this financial situation.
        Format your response as a list of tips without any introduction or conclusion.
        Use rupees (₹) as the currency in your response.
        """
        
        return cls.generate_response(prompt)
        
    @classmethod
    def detect_anomalies(cls, transaction_data):
        """
        Detect anomalies in transaction data using AI
        
        Args:
            transaction_data (list): List of transactions
            
        Returns:
            list: Detected anomalies with explanations
        """
        transactions_text = "\n".join([
            f"Date: {t.get('date', 'N/A')}, Category: {t.get('category', 'N/A')}, Amount: ₹{t.get('amount', 'N/A')}"
            for t in transaction_data
        ])
        
        prompt = f"""
        As a financial anomaly detection system, analyze the following transactions and identify any unusual patterns:
        
        {transactions_text}
        
        Please identify any potential anomalies in these transactions. For each anomaly, explain:
        1. The anomaly type (unusual amount, category, or frequency)
        2. Why it's considered unusual
        3. The specific transaction(s) involved
        
        Format your response as a JSON array with objects containing 'type', 'description', and 'transaction' fields.
        Use rupees (₹) as the currency in your response.
        """
        
        response = cls.generate_response(prompt)
        
        try:
            # Try to parse the response as JSON
            anomalies = json.loads(response)
            # Replace $ with ₹ in any strings
            for anomaly in anomalies:
                if isinstance(anomaly, dict):
                    for key in anomaly:
                        if isinstance(anomaly[key], str):
                            anomaly[key] = anomaly[key].replace('$', '₹')
            return anomalies
        except json.JSONDecodeError:
            # If response is not valid JSON, return it as a string
            return [{"type": "UNUSUAL_PATTERN", "description": response.replace('$', '₹'), "transaction": "N/A"}]
    
    @classmethod
    def generate_forecast(cls, historical_data, forecast_type):
        """
        Generate financial forecasts based on historical data
        
        Args:
            historical_data (list): Historical financial data
            forecast_type (str): Type of forecast (INCOME, EXPENSE, CASHFLOW)
            
        Returns:
            dict: Forecast results
        """
        data_text = "\n".join([
            f"Date: {entry.get('date', 'N/A')}, Amount: ₹{entry.get('amount', 'N/A')}"
            for entry in historical_data
        ])
        
        prompt = f"""
        As a financial forecasting system, analyze the following historical {forecast_type.lower()} data:
        
        {data_text}
        
        Please generate a forecast for the next 3 months based on this data.
        Include:
        1. Predicted amount for each month
        2. Confidence score (0.0-1.0)
        3. Brief explanation of the forecast
        
        Format your response as a JSON object with 'predictions' array and 'explanation' fields.
        Use rupees (₹) as the currency in your response.
        """
        
        response = cls.generate_response(prompt)
        
        try:
            # Try to parse the response as JSON
            forecast = json.loads(response)
            # Replace $ with ₹ in the explanation or any string fields
            if 'explanation' in forecast and isinstance(forecast['explanation'], str):
                forecast['explanation'] = forecast['explanation'].replace('$', '₹')
            return forecast
        except json.JSONDecodeError:
            # If response is not valid JSON, create a structured response
            return {
                "predictions": [
                    {"month": 1, "amount": 0, "confidence": 0.5}
                ],
                "explanation": response.replace('$', '₹')
            }
            
    @classmethod
    def financial_calculator(cls, query):
        """
        Process natural language financial calculations
        
        Args:
            query (str): User's financial calculation query
            
        Returns:
            dict: Calculation result with explanation
        """
        # Convert any $ to ₹ in the query
        query = query.replace('$', '₹')
        
        prompt = f"""
        As a financial calculator, solve the following query accurately and explain your reasoning:

        {query}

        For financial calculations, show step-by-step work and provide context about the calculation.
        If the question involves loans, interest rates, investments, taxes, or other financial concepts,
        provide additional insights about the financial implications.

        Format your response as a JSON object with:
        1. 'result': The direct answer to the calculation (a number or string)
        2. 'explanation': Step-by-step explanation of how you solved it
        3. 'insights': 1-2 bullet points with additional financial insights related to this calculation (if applicable)

        Make sure your calculations are numerically accurate.
        The response should be valid JSON without any markdown formatting or extra text before or after the JSON.
        
        IMPORTANT: Use rupees (₹) as the currency in your response, not dollars ($).
        """
        
        response = cls.generate_response(prompt, max_tokens=2048)
        
        try:
            # First try to parse the entire response as JSON
            calculation = json.loads(response)
            # Replace $ with ₹ in any string values
            for key in calculation:
                if isinstance(calculation[key], str):
                    calculation[key] = calculation[key].replace('$', '₹')
                elif isinstance(calculation[key], list):
                    calculation[key] = [item.replace('$', '₹') if isinstance(item, str) else item for item in calculation[key]]
            return calculation
        except json.JSONDecodeError:
            # Look for JSON block in the response
            try:
                # Check if response might contain a JSON block (often in markdown code blocks)
                if "```json" in response and "```" in response.split("```json", 1)[1]:
                    json_content = response.split("```json", 1)[1].split("```", 1)[0].strip()
                    calculation = json.loads(json_content)
                elif "```" in response and "```" in response.split("```", 1)[1]:
                    # Try with generic code block
                    json_content = response.split("```", 1)[1].split("```", 1)[0].strip()
                    calculation = json.loads(json_content)
                elif "{" in response and "}" in response:
                    # Try to extract JSON between the first { and last }
                    json_content = response[response.find('{'):response.rfind('}')+1]
                    calculation = json.loads(json_content)
                else:
                    # No JSON found
                    raise ValueError("No valid JSON found in response")
                
                # Replace $ with ₹ in any string values
                for key in calculation:
                    if isinstance(calculation[key], str):
                        calculation[key] = calculation[key].replace('$', '₹')
                    elif isinstance(calculation[key], list):
                        calculation[key] = [item.replace('$', '₹') if isinstance(item, str) else item for item in calculation[key]]
                
                return calculation
            except (ValueError, json.JSONDecodeError) as e:
                # If we still can't parse the JSON, create a structured response
                extracted_result = cls.extract_financial_result(response)
                return {
                    "result": extracted_result,
                    "explanation": response.replace('$', '₹'),
                    "insights": ["Please try rephrasing your question for better results."]
                } 