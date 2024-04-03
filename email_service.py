import imaplib, email, poplib
from settings import EMAIL_PROVIDERS, db_Host, db_Password, db_Name, db_User
from email.utils import parsedate_to_datetime, parseaddr
from email import policy
import mysql.connector
from mysql.connector import Error


def get_provider_servers(email_addr):
    domain = email_addr.split('@')[1].split('.')[0]
    if domain in EMAIL_PROVIDERS:
        imap_server = EMAIL_PROVIDERS[domain]['imap']
        pop3_server = EMAIL_PROVIDERS[domain]['pop3']
        return imap_server, pop3_server
    else:
        raise ValueError('Email provider not recognized. Please input server settings manually.')
print("get_provider_servers passed")
def has_attachments(email_message):
    attachment_count = 0
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
            continue
        attachment_count += 1
    return attachment_count > 0, attachment_count


def load_emails_from_inbox(email_addr, password):
    try:
        imap_server, pop3_server = get_provider_servers(email_addr)

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, password)
        mail.select('inbox')
        print('Successfully connected via IMAP')
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    email_message = email.message_from_bytes(data[0][1])
                    message_id = email_message.get('Message-ID')

                    is_attachment, attachment_count = has_attachments(email_message)

                    received_date = parsedate_to_datetime(email_message['Date'])
                    sender_email = email.utils.parseaddr(email_message['From'])[1]
                    subject = email_message['Subject']
                    recipient_email = email.utils.parseaddr(email_message['To'])[1]
    except:
        try:
            _, pop3_server=get_provider_servers(email_addr)
            pop3_mail = poplib.POP3_SSL(pop3_server)
            pop3_mail.user(email_addr)
            pop3_mail.pass_(password)
            print('Successfully connected via POP3')
            message_count, mailbox_size = pop3_mail.stat()
            for i in range(message_count):
                response, lines, octects = pop3_mail.retr(i + 1)
                raw_email = b'\n'.join(lines)
                email_message = email.message_from_bytes(raw_email, policy=policy.default)
                message_id = email_message.get('Message-ID')
                is_attachment, attachment_count = has_attachments(email_message)

                received_date = parsedate_to_datetime(email_message['Date'])
                sender_email = parseaddr(email_message['From'])[1]
                subject = email_message['Subject']
                recipient_email = parseaddr(email_message['To'])[1]
        except Exception as e:
            print('Failed to connect via both IMAP and POP3')
        print('second stage checked')


    try:
        db_connection = mysql.connector.connect(
            host=db_Host,
            user=db_User,
            password=db_Password,
            database=db_Name
            )

        db_cursor = db_connection.cursor()

        create_table_sql = """
            CREATE TABLE IF NOT EXISTS email_tab (
                email_id INT AUTO_INCREMENT PRIMARY KEY,
                received_date DATETIME NOT NULL,
                sender_email VARCHAR(255) NOT NULL,
                subject VARCHAR(255),
                email_body TEXT,
                has_attachments BOOLEAN,
                attachment_count INT,
                recipient_email VARCHAR(255) NOT NULL,
                message_id VARCHAR(255) NOT NULL UNIQUE
            );"""

        db_cursor.execute(create_table_sql)
        db_connection.commit()
        print("Table 'emails' checked/created successfully.")


        db_cursor.execute("SELECT * FROM email_tab WHERE message_id = %s ", (message_id,))
        if db_cursor.fetchone() is None:
            insert_sql = """
                INSERT INTO email_tab(received_date, sender_email, subject, has_attachments, attachment_count, recipient_email, message_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            values = (received_date, sender_email, subject, is_attachment, attachment_count, recipient_email, message_id)
            db_cursor.execute(insert_sql, values)
            db_connection.commit()

    except Error as e:
        print("Error while connecting to MySQL:", e)
        return False

    finally:
        if db_connection.is_connected():
            db_info = db_connection.get_server_info()
            print('Connection to MYSQL server: ', db_info)
            db_cursor.close()
            db_connection.close()
    return True


def get_email(email_id):
    cnx = mysql.connector.connect(
        host=db_Host,
        user=db_User,
        password=db_Password,
        database=db_Name
    )
    cursor = cnx.cursor()

    query = f"SELECT * FROM email_tab WHERE email_id = {email_id}"
    cursor.execute(query)

    email = None
    for row in cursor:
        email = row
    cnx.close()

    return email
