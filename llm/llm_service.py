import os

import time
from openai import OpenAI
from dotenv import load_dotenv

# Make sure .env is loaded
load_dotenv()

class LLMService:
    """Service for interacting with LLMs"""
    
    def __init__(self, config):
        self.provider = config.get("provider", "openai")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.1)
        self.rate_limit = config.get("rate_limit", False)
        self.max_tokens = config.get("max_tokens", 1000)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay = config.get("retry_delay", 5)
        
        # Set API key for OpenAI
        if self.provider == "openai":
            # Try to get API key from config
            api_key = config.get("api_key", "")
            
            # If not in config, try environment variable
            if not api_key:
                api_key = os.environ.get("OPENAI_API_KEY", "")
            
            if not api_key:
                print("Warning: OpenAI API key not found. Using mock responses.")
                self.use_mock = True
                self.client = None
            else:
                if self.rate_limit:
                    print("OpenAI API key configured with rate limiting (free tier mode).")
                else:
                    print("OpenAI API key configured.")
                self.client = OpenAI(api_key=api_key)
                self.use_mock = False
        else:
            self.use_mock = True
            self.client = None
    
    def generate(self, prompt):
        """Generate text using the configured LLM"""
        if self.provider == "openai" and not self.use_mock and self.client:
            return self._generate_openai(prompt)
        else:
            # Fallback to mock responses for demo purposes
            return self._generate_mock(prompt)
    
    def _generate_openai(self, prompt):
        """Generate text using OpenAI API with retry logic for free tier"""
        attempts = 0
        
        while attempts <= self.retry_attempts:
            try:
                # Add a small delay if rate limiting is enabled
                if self.rate_limit and attempts > 0:
                    print(f"Rate limit pause: waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                
                # Make API call with controlled token usage
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
            
            except Exception as e:
                attempts += 1
                if "rate limit" in str(e).lower():
                    wait_time = self.retry_delay * attempts
                    print(f"Rate limit reached. Waiting {wait_time} seconds before retry. Attempt {attempts}/{self.retry_attempts}")
                    time.sleep(wait_time)
                else:
                    print(f"Error with OpenAI API: {e}")
                    if attempts >= self.retry_attempts:
                        print("Maximum retry attempts reached. Using mock response.")
                        return self._generate_mock(prompt)
        
        return self._generate_mock(prompt)
        
    def _generate_mock(self, prompt):
        """Generate mock responses for demo purposes"""
        if "analyze" in prompt.lower():
            return """
# Code Analysis Report

## Overview
This appears to be a COBOL program that processes customer transactions.

## Key Components
1. DATA DIVISION - Contains file descriptions and working storage
2. PROCEDURE DIVISION - Contains the main logic
3. Several subroutines for processing different types of transactions

## Dependencies
- References external files: CUSTMAST, TRANFILE
- Likely depends on CICS environment

## Recommendations
- Consider refactoring complex IF/ELSE blocks
- Transaction processing logic could be modernized using microservices
- Database access should be replaced with modern alternatives
            """
        
        elif "document" in prompt.lower():
            return """
# Program Documentation

## Purpose
This program processes customer transactions against the customer master file.

## Inputs
- CUSTMAST: Customer master file
- TRANFILE: Transaction input file

## Outputs
- Updated customer master file
- PRNTFILE: Report of processed transactions

## Processing Logic
1. Read transaction records
2. For each transaction:
   - Look up customer in master file
   - Apply transaction based on type
   - Update master record
3. Generate summary report

## Error Handling
The program includes error handling for:
- Invalid customer numbers
- Transaction amount limits
- File I/O errors
            """
        
        elif "transform" in prompt.lower():
            return """
import java.io.*;
import java.util.*;

/**
 * CustomerTransactionProcessor - Transformed from COBOL
 * Processes customer transactions against master file
 */
public class CustomerTransactionProcessor {
    
    private static final String CUSTOMER_FILE = "customers.dat";
    private static final String TRANSACTION_FILE = "transactions.dat";
    
    private List<Customer> customers = new ArrayList<>();
    
    public static void main(String[] args) {
        CustomerTransactionProcessor processor = new CustomerTransactionProcessor();
        processor.loadCustomerFile();
        processor.processTransactions();
        processor.saveCustomerFile();
    }
    
    public void loadCustomerFile() {
        // Load customer master file
        try (BufferedReader reader = new BufferedReader(new FileReader(CUSTOMER_FILE))) {
            String line;
            while ((line = reader.readLine()) != null) {
                customers.add(Customer.fromString(line));
            }
        } catch (IOException e) {
            System.err.println("Error reading customer file: " + e.getMessage());
        }
    }
    
    public void processTransactions() {
        // Process transaction file
        try (BufferedReader reader = new BufferedReader(new FileReader(TRANSACTION_FILE))) {
            String line;
            while ((line = reader.readLine()) != null) {
                Transaction transaction = Transaction.fromString(line);
                processTransaction(transaction);
            }
        } catch (IOException e) {
            System.err.println("Error reading transaction file: " + e.getMessage());
        }
    }
    
    private void processTransaction(Transaction transaction) {
        // Find customer record
        Optional<Customer> customerOpt = customers.stream()
                .filter(c -> c.getCustomerId().equals(transaction.getCustomerId()))
                .findFirst();
                
        if (customerOpt.isPresent()) {
            Customer customer = customerOpt.get();
            switch (transaction.getType()) {
                case "ADD":
                    customer.setBalance(customer.getBalance() + transaction.getAmount());
                    break;
                case "SUBTRACT":
                    customer.setBalance(customer.getBalance() - transaction.getAmount());
                    break;
                default:
                    System.err.println("Unknown transaction type: " + transaction.getType());
            }
        } else {
            System.err.println("Customer not found: " + transaction.getCustomerId());
        }
    }
    
    public void saveCustomerFile() {
        // Save updated customer file
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(CUSTOMER_FILE))) {
            for (Customer customer : customers) {
                writer.write(customer.toString());
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error writing customer file: " + e.getMessage());
        }
    }
}
            """
        
        return "Mock response for: " + prompt[:50] + "..."
