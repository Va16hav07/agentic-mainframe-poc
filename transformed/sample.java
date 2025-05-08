
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
            