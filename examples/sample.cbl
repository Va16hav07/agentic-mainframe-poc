       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTUPDT.
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CUSTMAST ASSIGN TO CUSTFILE
               ORGANIZATION IS INDEXED
               ACCESS IS RANDOM
               RECORD KEY IS CM-CUST-ID
               FILE STATUS IS CM-STATUS.
           SELECT TRANFILE ASSIGN TO TRANFILE
               ORGANIZATION IS SEQUENTIAL
               FILE STATUS IS TR-STATUS.
           SELECT PRNTFILE ASSIGN TO PRNTFILE
               ORGANIZATION IS SEQUENTIAL
               FILE STATUS IS PR-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  CUSTMAST.
       01  CUST-RECORD.
           05  CM-CUST-ID          PIC X(6).
           05  CM-FIRST-NAME       PIC X(20).
           05  CM-LAST-NAME        PIC X(30).
           05  CM-ADDRESS          PIC X(50).
           05  CM-CITY             PIC X(20).
           05  CM-STATE            PIC X(2).
           05  CM-ZIP-CODE         PIC X(10).
           05  CM-ACCOUNT-BALANCE  PIC S9(7)V99.
           05  CM-LAST-ACTIVITY    PIC X(8).
       
       FD  TRANFILE.
       01  TRAN-RECORD.
           05  TR-TRAN-CODE        PIC X(1).
               88  TR-ADD-TRAN     VALUE 'A'.
               88  TR-UPDATE-TRAN  VALUE 'U'.
               88  TR-DELETE-TRAN  VALUE 'D'.
           05  TR-CUST-ID          PIC X(6).
           05  TR-TRAN-AMOUNT      PIC S9(7)V99.
           05  TR-TRAN-DATE        PIC X(8).
       
       FD  PRNTFILE.
       01  PRINT-RECORD            PIC X(132).
       
       WORKING-STORAGE SECTION.
       01  WS-WORK-AREAS.
           05  CM-STATUS           PIC X(2).
           05  TR-STATUS           PIC X(2).
           05  PR-STATUS           PIC X(2).
           05  WS-EOF              PIC X(1) VALUE 'N'.
               88  END-OF-FILE     VALUE 'Y'.
           05  WS-RECORD-COUNT     PIC 9(5) VALUE 0.
           05  WS-ERROR-COUNT      PIC 9(5) VALUE 0.
       
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-INIT.
           PERFORM 2000-PROCESS UNTIL END-OF-FILE.
           PERFORM 3000-CLOSE.
           STOP RUN.
       
       1000-INIT.
           OPEN I-O    CUSTMAST.
           OPEN INPUT  TRANFILE.
           OPEN OUTPUT PRNTFILE.
           
           IF CM-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING CUSTOMER FILE: ' CM-STATUS
               MOVE 'Y' TO WS-EOF
           END-IF.
           
           IF TR-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING TRANSACTION FILE: ' TR-STATUS
               MOVE 'Y' TO WS-EOF
           END-IF.
           
           IF PR-STATUS NOT = '00'
               DISPLAY 'ERROR OPENING PRINT FILE: ' PR-STATUS
               MOVE 'Y' TO WS-EOF
           END-IF.
           
           IF NOT END-OF-FILE
               READ TRANFILE
                   AT END MOVE 'Y' TO WS-EOF
               END-READ
           END-IF.
       
       2000-PROCESS.
           EVALUATE TRUE
               WHEN TR-ADD-TRAN
                   PERFORM 2100-ADD-CUSTOMER
               WHEN TR-UPDATE-TRAN
                   PERFORM 2200-UPDATE-CUSTOMER
               WHEN TR-DELETE-TRAN
                   PERFORM 2300-DELETE-CUSTOMER
               WHEN OTHER
                   DISPLAY 'INVALID TRANSACTION CODE: ' TR-TRAN-CODE
                   ADD 1 TO WS-ERROR-COUNT
           END-EVALUATE.
           
           READ TRANFILE
               AT END MOVE 'Y' TO WS-EOF
           END-READ.
       
       2100-ADD-CUSTOMER.
           MOVE TR-CUST-ID TO CM-CUST-ID.
           READ CUSTMAST
               INVALID KEY
                   PERFORM 2110-CREATE-NEW-CUSTOMER
               NOT INVALID KEY
                   DISPLAY 'ERROR: CUSTOMER ALREADY EXISTS: ' CM-CUST-ID
                   ADD 1 TO WS-ERROR-COUNT
           END-READ.
       
       2110-CREATE-NEW-CUSTOMER.
           INITIALIZE CUST-RECORD.
           MOVE TR-CUST-ID TO CM-CUST-ID.
           MOVE TR-TRAN-AMOUNT TO CM-ACCOUNT-BALANCE.
           MOVE TR-TRAN-DATE TO CM-LAST-ACTIVITY.
           
           WRITE CUST-RECORD
               INVALID KEY
                   DISPLAY 'ERROR CREATING CUSTOMER: ' CM-CUST-ID
                   ADD 1 TO WS-ERROR-COUNT
               NOT INVALID KEY
                   ADD 1 TO WS-RECORD-COUNT
           END-WRITE.
       
       2200-UPDATE-CUSTOMER.
           MOVE TR-CUST-ID TO CM-CUST-ID.
           READ CUSTMAST
               INVALID KEY
                   DISPLAY 'ERROR: CUSTOMER NOT FOUND: ' CM-CUST-ID
                   ADD 1 TO WS-ERROR-COUNT
               NOT INVALID KEY
                   ADD TR-TRAN-AMOUNT TO CM-ACCOUNT-BALANCE
                   MOVE TR-TRAN-DATE TO CM-LAST-ACTIVITY
                   
                   REWRITE CUST-RECORD
                       INVALID KEY
                           DISPLAY 'ERROR UPDATING CUSTOMER: ' CM-CUST-ID
                           ADD 1 TO WS-ERROR-COUNT
                       NOT INVALID KEY
                           ADD 1 TO WS-RECORD-COUNT
                   END-REWRITE
           END-READ.
       
       2300-DELETE-CUSTOMER.
           MOVE TR-CUST-ID TO CM-CUST-ID.
           DELETE CUSTMAST
               INVALID KEY
                   DISPLAY 'ERROR: CUSTOMER NOT FOUND FOR DELETE: ' 
                       CM-CUST-ID
                   ADD 1 TO WS-ERROR-COUNT
               NOT INVALID KEY
                   ADD 1 TO WS-RECORD-COUNT
           END-DELETE.
       
       3000-CLOSE.
           CLOSE CUSTMAST.
           CLOSE TRANFILE.
           
           MOVE SPACES TO PRINT-RECORD.
           STRING 'PROCESSING COMPLETE. RECORDS PROCESSED: ' 
                  WS-RECORD-COUNT
                  ' ERRORS: '
                  WS-ERROR-COUNT
               DELIMITED BY SIZE
               INTO PRINT-RECORD.
           
           WRITE PRINT-RECORD.
           CLOSE PRNTFILE.
