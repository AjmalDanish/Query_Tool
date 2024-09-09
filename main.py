import sys
import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QDateEdit, QDialog, QLineEdit, 
                             QFormLayout, QMessageBox, QListWidget, QHeaderView, QSizePolicy, QPlainTextEdit,
                             QMainWindow, QAbstractItemView,QScrollArea)
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt5.QtGui import QColor, QPalette, QFont
import json
import re
import os
from datetime import datetime, date, timedelta
import sqlite3

class ScheduleQueryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schedule Query")
        layout = QVBoxLayout()

        self.query_input = QTextEdit()
        layout.addWidget(QLabel("Query:"))
        layout.addWidget(self.query_input)

        interval_layout = QHBoxLayout()
        self.interval_input = QLineEdit()
        self.interval_unit = QComboBox()
        self.interval_unit.addItems(["Minutes", "Hours", "Days"])
        interval_layout.addWidget(QLabel("Run every:"))
        interval_layout.addWidget(self.interval_input)
        interval_layout.addWidget(self.interval_unit)
        layout.addLayout(interval_layout)

        self.output_file = QLineEdit()
        layout.addWidget(QLabel("Output file name (without .csv):"))
        layout.addWidget(self.output_file)

        self.schedule_button = QPushButton("Schedule")
        self.schedule_button.clicked.connect(self.accept)
        layout.addWidget(self.schedule_button)

        self.setLayout(layout)

class NotificationWidget(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            border-radius: 15px;
            padding: 20px;
        """)
        self.setMinimumSize(300, 100)  # Set minimum size
        
        layout = QVBoxLayout()
        self.label = QLabel(message)
        font = QFont()
        font.setPointSize(12)  # Increase font size
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(3000)  # Close after 3 seconds

class StyleHelper:
    @staticmethod
    def set_dark_theme(app):
        app.setStyle("Fusion")
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)

    @staticmethod
    def style_button(button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #2ecc71;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    @staticmethod
    def style_combo_box(combo):
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 5px;
                min-width: 6em;
                background-color: #34495e;
                color: #e9ebed;
                font-weight: bold;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
            }
        """)

    @staticmethod
    def style_text_edit(text_edit):
        text_edit.setStyleSheet("""
            QTextEdit, QPlainTextEdit {
                background-color: #000000;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 5px;
                font-family: Courier;
            }
        """)

class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton {
                background-color: #345CD3;
                color: #EAEEFA;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def enterEvent(self, event):
        self.animate_color(QColor(41, 128, 185))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_color(QColor(52, 152, 219))
        super().leaveEvent(event)

    def animate_color(self, end_color):
        start_color = self.palette().color(QPalette.Button)
        animation = QPropertyAnimation(self, b"color")
        animation.setStartValue(start_color)
        animation.setEndValue(end_color)
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    def setColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Button, color)
        self.setPalette(palette)

    color = pyqtProperty(QColor, fset=setColor)

class ScriptDialog(QDialog):
    def __init__(self, script, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Python Script")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        self.script_text = QPlainTextEdit()
        self.script_text.setPlainText(script)
        self.script_text.setReadOnly(True)
        StyleHelper.style_text_edit(self.script_text)
        layout.addWidget(self.script_text)
        
        download_btn = AnimatedButton("Download Script")
        download_btn.clicked.connect(self.download_script)
        layout.addWidget(download_btn)
        
        self.setLayout(layout)

    def download_script(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Python Script", "", "Python Files (*.py);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'w') as f:
                f.write(self.script_text.toPlainText())
            QMessageBox.information(self, "Download Complete", f"Python script saved as {fileName}")
class AddDatabaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Database")
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #ecf0f1;
            }
        """)
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.host_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.database_input = QLineEdit()
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Host:", self.host_input)
        layout.addRow("User:", self.user_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Database:", self.database_input)
        
        buttons = QHBoxLayout()
        self.ok_button = AnimatedButton("OK")
        self.cancel_button = AnimatedButton("Cancel")
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        
        layout.addRow(buttons)
        self.setLayout(layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_df = None
        self.load_db_configs()
        self.query_history = {}
        self.init_history_db()
        self.scheduled_queries = []
        self.initUI()
        self.load_scheduled_queries()
        self.start_scheduler()

    def load_db_configs(self):
        try:
            with open('db_configs.json', 'r') as f:
                self.db_configs = json.load(f)
        except FileNotFoundError:
            self.db_configs = [
            {
                "name": "Db1",
                "host": "",
                "user": "",
                "password": "",
                "database": ""
            },
            {
                "name": "DB2",
                "host": "",
                "port": 3306,
                "user": "",
                "password": "",
                "database": "",
                "ssl_ca": "cacert.pem"
            }
        ]

    def save_db_configs(self):
        with open('db_configs.json', 'w') as f:
            json.dump(self.db_configs, f)


    def initUI(self):
        self.setWindowTitle('Database Query Tool')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)

        # Database selection and add new database button
        db_layout = QHBoxLayout()
        self.db_combo = QComboBox()
        StyleHelper.style_combo_box(self.db_combo)
        self.update_db_combo()
        db_layout.addWidget(self.db_combo)
        
        add_db_btn = AnimatedButton('Add New Database')
        add_db_btn.clicked.connect(self.add_new_database)
        db_layout.addWidget(add_db_btn)
        main_layout.addLayout(db_layout)

        # Date range selection
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit(calendarPopup=True)
        self.end_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date)
        main_layout.addLayout(date_layout)

        # Query input
        self.query_input = QTextEdit()
        StyleHelper.style_text_edit(self.query_input)
        self.query_input.setPlaceholderText("Enter your SQL query here...")
        main_layout.addWidget(self.query_input)

        # Buttons
        button_layout = QHBoxLayout()
        buttons = [
            ('Use Predefined Query', self.use_predefined_query),
            ('Execute Query', self.execute_query),
            ('Show Query History', self.show_query_history),
            ('Generate Python Script', self.generate_python_script)
        ]
        for text, slot in buttons:
            btn = AnimatedButton(text)
            btn.clicked.connect(slot)
            button_layout.addWidget(btn)
            if text == 'Generate Python Script':
                self.generate_script_btn = btn
                self.generate_script_btn.setEnabled(False)
        main_layout.addLayout(button_layout)

        # Schedule Query, View Scheduled Queries, and View Saved Results buttons
        schedule_layout = QHBoxLayout()
        schedule_buttons = [
            ('Schedule Query', self.schedule_query),
            ('View Scheduled Queries', self.view_scheduled_queries),
            ('View Saved Results', self.view_saved_results)
        ]
        for text, slot in schedule_buttons:
            btn = AnimatedButton(text)
            btn.clicked.connect(slot)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            schedule_layout.addWidget(btn)
        main_layout.addLayout(schedule_layout)

        self.table = QTableWidget()
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable table's vertical scrollbar
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable table's horizontal scrollbar

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Apply table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #e9ebed;
                color: #000000;
                gridline-color: #7f8c8d;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 5px;
                border: 1px solid #7f8c8d;
            }
            QScrollBar:horizontal {
                border: 1px solid #2c3e50;
                background: #34495e;
                height: 15px;
                margin: 0px 22px 0px 22px;
            }
            QScrollBar::handle:horizontal {
                background: #3498db;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: 1px solid #2c3e50;
                background: #2c3e50;
                width: 20px;
                subcontrol-origin: margin;
            }
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                border: 1px solid #2c3e50;
                width: 3px;
                height: 3px;
                background: white;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        

        # Shape information
        self.shape_label = QLabel()
        main_layout.addWidget(self.shape_label)

        # Download button
        self.download_btn = AnimatedButton('Download Results')
        self.download_btn.clicked.connect(self.download_results)
        main_layout.addWidget(self.download_btn)

        # Set spacing and margins for the main layout
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

    def update_db_combo(self):
        self.db_combo.clear()
        self.db_combo.addItems([db["name"] for db in self.db_configs])

    def add_new_database(self):
        dialog = AddDatabaseDialog(self)
        if dialog.exec_():
            new_db = {
                "name": dialog.name_input.text(),
                "host": dialog.host_input.text(),
                "user": dialog.user_input.text(),
                "password": dialog.password_input.text(),
                "database": dialog.database_input.text()
            }
            self.db_configs.append(new_db)
            self.save_db_configs()
            self.update_db_combo()

    def use_predefined_query(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        predefined_query = f"""
        SELECT * FROM `cta_report` 
        WHERE `added_on` BETWEEN '{start_date} 00:00:00.000000' AND '{end_date} 23:59:59.999999'
        """
        self.query_input.setPlainText(predefined_query)
        
    def display_results(self, df):
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.table.setItem(i, j, item)

        # Resize columns to contents
        self.table.resizeColumnsToContents()

        # Adjust column widths if they're too narrow
        min_width = 100  # Minimum width in pixels
        for col in range(self.table.columnCount()):
            if self.table.columnWidth(col) < min_width:
                self.table.setColumnWidth(col, min_width)

        # Set the table size to fit its contents
        self.table.resizeRowsToContents()
        table_width = sum(self.table.columnWidth(c) for c in range(self.table.columnCount())) + self.table.verticalHeader().width()
        table_height = sum(self.table.rowHeight(r) for r in range(self.table.rowCount())) + self.table.horizontalHeader().height()
        self.table.setFixedSize(table_width, table_height)

        self.shape_label.setText(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")


    def download_results(self):
        if self.current_df is not None:
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if fileName:
                self.current_df.to_csv(fileName, index=False)
                QMessageBox.information(self, "Download Complete", f"File saved as {fileName}")

    def init_history_db(self):
        self.history_db = sqlite3.connect('query_history.db')
        cursor = self.history_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             timestamp DATETIME,
             database TEXT,
             query TEXT)
        ''')
        self.history_db.commit()
    
    def add_to_history(self, query):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        cursor = self.history_db.cursor()
        cursor.execute('''
            INSERT INTO query_history (timestamp, database, query)
            VALUES (?, ?, ?)
        ''', (datetime.now().strftime(DATETIME_FORMAT), self.db_combo.currentText(), query))
        self.history_db.commit()

    def show_query_history(self):
        dialog = QueryHistoryDialog(self.history_db, self)
        dialog.exec_()

    def is_read_only_query(self, query):
        # List of allowed keywords
        allowed_keywords = ['select', 'show', 'describe', 'desc', 'explain']
        
        # Remove comments and split the query into words
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        words = re.findall(r'\b\w+\b', clean_query.lower())
        
        # Check if the first word is in the allowed list
        if words and words[0] not in allowed_keywords:
            return False
        
        # Additional checks for prohibited operations
        prohibited_keywords = ['create', 'alter', 'drop', 'insert', 'update', 'delete', 'truncate', 'rename', 'replace', 'load']
        if any(word in prohibited_keywords for word in words):
            return False
        
        return True

    def execute_query(self):
        db_config = self.db_configs[self.db_combo.currentIndex()]
        query = self.query_input.toPlainText()

        if not self.is_read_only_query(query):
            QMessageBox.warning(self, "Read-Only Access", 
                                "This system is for read-only access. Only SELECT, SHOW, DESCRIBE, and EXPLAIN queries are allowed.")
            return

        connection_config = {k: v for k, v in db_config.items() if k != 'name'}

        try:
            # Check if SSL is required
            if db_config.get('requires_ssl', False):
                connection_config['ssl_ca'] = db_config.get('ssl_ca')
                connection_config['ssl_verify_cert'] = True

            connection = mysql.connector.connect(**connection_config)
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            
            self.current_df = pd.DataFrame(result, columns=columns)
            self.display_results(self.current_df)
            
            cursor.close()
            connection.close()

            # Add query to history
            self.add_to_history(query)  # Use the add_to_history method
            self.show_success_notification("Query executed successfully!")
            self.generate_script_btn.setEnabled(True)  # Enable the Generate Script button

        except mysql.connector.Error as error:
            if isinstance(error, mysql.connector.ProgrammingError):
                QMessageBox.warning(self, "Query Error", f"Syntax error in your SQL query: {error}")
            elif isinstance(error, mysql.connector.IntegrityError):
                QMessageBox.warning(self, "Data Integrity Error", f"The query violates database integrity constraints: {error}")
            elif isinstance(error, mysql.connector.OperationalError):
                QMessageBox.critical(self, "Connection Error", f"Unable to connect to the database. Please check your network connection and database settings: {error}")
            else:
                QMessageBox.critical(self, "Query Error", f"An unexpected error occurred: {error}")
            self.generate_script_btn.setEnabled(False)


    def show_success_notification(self, message):
        notification = NotificationWidget(message, self)
        geometry = self.geometry()
        notification.move(geometry.right() - notification.width() - 50, 
                        geometry.top() + 50)
        notification.show()

    def generate_python_script(self):
        if not self.query_input.toPlainText():
            QMessageBox.warning(self, "No Query", "Please enter a query first.")
            return

        query = self.query_input.toPlainText().strip()
        
        if not self.is_read_only_query(query):
            QMessageBox.warning(self, "Read-Only Access", 
                                "This system is for read-only access. You cannot generate scripts for non-SELECT operations.")
            return

        db_config = self.db_configs[self.db_combo.currentIndex()]
        
        # Check if SSL is required
        requires_ssl = db_config.get('requires_ssl', False)
        
        ssl_config = ""
        if requires_ssl:
            ssl_config = f"""
            # SSL Configuration
            ssl_args = {{
                'ssl': {{
                    'ca': '{db_config['ssl_ca']}',
                    'check_hostname': True
                }}
            }}
            """
        else:
            ssl_config = "ssl_args = {}"

        script_template = f"""
    import pymysql
    import pandas as pd

    # Database connection details
    host = '{db_config["host"]}'
    user = '{db_config["user"]}'
    password = '{db_config["password"]}'
    database = '{db_config["database"]}'

    {ssl_config}

    # Establish a connection to the database
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        **ssl_args
    )

    # Create a cursor to execute SQL queries
    cursor = connection.cursor()

    # SQL query
    sql_template = '''
    {query}
    '''

    # Set chunk size
    chunk_size = 100000
    offset = 0
    all_rows = []

    # Loop until all rows are fetched
    while True:
        # Execute the query with LIMIT and OFFSET
        cursor.execute(sql_template + ' LIMIT %s OFFSET %s', (chunk_size, offset))
        
        # Fetch the rows
        rows = cursor.fetchall()
        
        # Break the loop if no more rows are returned
        if not rows:
            break
        
        # Append the fetched rows to the list
        all_rows.extend(rows)
        
        # Increment the offset for the next iteration
        offset += chunk_size

    # Get the column names
    columns = [col[0] for col in cursor.description]

    # Close the cursor and the database connection
    cursor.close()
    connection.close()

    # Create a DataFrame
    result_df = pd.DataFrame(all_rows, columns=columns)

    # Display the shape of the DataFrame
    print(f"Shape of the result: {{result_df.shape}}")

    # Display the first few rows of the DataFrame
    print(result_df.head())

    # Optionally, save the DataFrame to a CSV file
    # result_df.to_csv('query_results.csv', index=False)

    # Display the DataFrame
    result_df
    """

        script_dialog = ScriptDialog(script_template, self)
        script_dialog.exec_()

    def load_scheduled_queries(self):
        try:
            with open('scheduled_queries.json', 'r') as f:
                self.scheduled_queries = json.load(f)
            
            # Convert any float timestamps to strings and add missing keys
            for query in self.scheduled_queries:
                if isinstance(query['next_run'], float):
                    query['next_run'] = datetime.fromtimestamp(query['next_run']).isoformat()
                if 'output_file' not in query:
                    query['output_file'] = 'default_output'
                if 'database' not in query:
                    if self.db_combo.count() > 0:
                        query['database'] = self.db_combo.itemText(0)  # Use the first database as default
                    else:
                        query['database'] = "No database available"  # Or some other default value
            
            # Save the updated queries
            self.save_scheduled_queries()
        except FileNotFoundError:
            self.scheduled_queries = []

    def save_scheduled_queries(self):
        with open('scheduled_queries.json', 'w') as f:
            json.dump(self.scheduled_queries, f)

    def start_scheduler(self):
        self.scheduler_timer = QTimer(self)
        self.scheduler_timer.timeout.connect(self.check_scheduled_queries)
        self.scheduler_timer.start(60000)  # Check every minute

    def check_scheduled_queries(self):
        current_time = datetime.now()
        for query in self.scheduled_queries:
            next_run = datetime.fromisoformat(query['next_run'])
            if current_time >= next_run:
                self.run_scheduled_query(query)
                query['next_run'] = (current_time + timedelta(seconds=query['interval'])).isoformat()
        self.save_scheduled_queries()

    def run_scheduled_query(self, query):
        database = query.get('database', self.db_combo.itemText(0))  # Use first database as default
        db_index = self.db_combo.findText(database)
        if db_index == -1:
            self.show_error_notification(f"Database '{database}' not found. Using default.")
            db_index = 0

        db_config = self.db_configs[db_index]
        connection_config = {k: v for k, v in db_config.items() if k != 'name'}

        try:
            connection = mysql.connector.connect(**connection_config)
            cursor = connection.cursor()
            cursor.execute(query['query'])
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            
            df = pd.DataFrame(result, columns=columns)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{query['output_file']}_{timestamp}.csv"
            df.to_csv(filename, index=False)
            
            cursor.close()
            connection.close()

            self.show_success_notification(f"Scheduled query executed and saved as {filename}")
        except mysql.connector.Error as error:
            self.show_error_notification(f"Error executing scheduled query: {error}")

    def schedule_query(self):
        dialog = ScheduleQueryDialog(self)
        if dialog.exec_():
            query = dialog.query_input.toPlainText()
            interval = int(dialog.interval_input.text())
            unit = dialog.interval_unit.currentText()
            output_file = dialog.output_file.text() or 'default_output'  # Provide a default if empty

            if unit == "Minutes":
                interval *= 60
            elif unit == "Hours":
                interval *= 3600
            else:  # Days
                interval *= 86400

            next_run = (datetime.now() + timedelta(seconds=interval)).isoformat()

            self.scheduled_queries.append({
                'query': query,
                'interval': interval,
                'next_run': next_run,
                'output_file': output_file,
                'database': self.db_combo.currentText()
            })
            self.save_scheduled_queries()
            self.show_success_notification("Query scheduled successfully")

    def view_scheduled_queries(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Scheduled Queries")
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(5)  # Add one more column for database
        table.setHorizontalHeaderLabels(["Query", "Interval", "Next Run", "Output File", "Database"])
        
        for query in self.scheduled_queries:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(query['query']))
            table.setItem(row, 1, QTableWidgetItem(f"{query['interval']} seconds"))
            
            next_run = query['next_run']
            if isinstance(next_run, float):
                next_run = datetime.fromtimestamp(next_run).isoformat()
            table.setItem(row, 2, QTableWidgetItem(str(next_run)))
            
            output_file = query.get('output_file', 'Not specified')
            table.setItem(row, 3, QTableWidgetItem(output_file))
            
            database = query.get('database', 'Not specified')
            table.setItem(row, 4, QTableWidgetItem(database))

        layout.addWidget(table)
        dialog.exec_()

    def view_saved_results(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Query Results")
        layout = QVBoxLayout()
        list_widget = QListWidget()

        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        list_widget.addItems(csv_files)

        open_button = QPushButton("Open Selected File")
        open_button.clicked.connect(lambda: self.open_csv_file(list_widget.currentItem().text()))

        layout.addWidget(list_widget)
        layout.addWidget(open_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def open_csv_file(self, filename):
        if filename:
            df = pd.read_csv(filename)
            self.display_results(df)
            self.show_success_notification(f"Loaded results from {filename}")

    def show_success_notification(self, message):
        notification = NotificationWidget(message, self)
        geometry = self.geometry()
        notification.move(geometry.right() - notification.width() - 50, 
                        geometry.top() + 50)
        notification.show()

    def show_error_notification(self, message):
        QMessageBox.critical(self, "Error", message)

class QueryHistoryDialog(QDialog):
    def __init__(self, history_db, parent=None):
        super().__init__(parent)
        self.history_db = history_db
        self.page_size = 50
        self.current_page = 0
        self.total_pages = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Query History")
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout(self)

        # Search and filter controls
        filter_layout = QHBoxLayout()

        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        filter_layout.addWidget(QLabel("Start Date:"))
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("End Date:"))
        filter_layout.addWidget(self.end_date)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search queries...")
        filter_layout.addWidget(self.search_input)

        self.db_filter = QComboBox()
        self.db_filter.addItem("All Databases")
        self.db_filter.addItems(self.get_database_list())
        filter_layout.addWidget(QLabel("Database:"))
        filter_layout.addWidget(self.db_filter)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.update_history)
        filter_layout.addWidget(search_btn)

        layout.addLayout(filter_layout)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Database", "Query", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_btn)

        self.page_label = QLabel()
        pagination_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)

        layout.addLayout(pagination_layout)

        self.setLayout(layout)

        # Initial load
        self.update_history()

    def get_database_list(self):
        cursor = self.history_db.cursor()
        cursor.execute("SELECT DISTINCT database FROM query_history ORDER BY database")
        return [row[0] for row in cursor.fetchall()]

    def update_history(self):
        self.current_page = 0
        self.load_page()

    def load_page(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        search_term = self.search_input.text()
        selected_db = self.db_filter.currentText()

        cursor = self.history_db.cursor()
        
        # Count total matching rows
        count_query = """
            SELECT COUNT(*) FROM query_history 
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_date, end_date + " 23:59:59"]

        if search_term:
            count_query += " AND query LIKE ?"
            params.append(f"%{search_term}%")

        if selected_db != "All Databases":
            count_query += " AND database = ?"
            params.append(selected_db)

        cursor.execute(count_query, params)
        total_rows = cursor.fetchone()[0]
        self.total_pages = (total_rows - 1) // self.page_size + 1

        # Fetch page data
        offset = self.current_page * self.page_size
        data_query = f"""
            SELECT timestamp, database, query FROM query_history 
            WHERE timestamp BETWEEN ? AND ?
        """
        if search_term:
            data_query += " AND query LIKE ?"
        if selected_db != "All Databases":
            data_query += " AND database = ?"
        data_query += f" ORDER BY timestamp DESC LIMIT {self.page_size} OFFSET {offset}"

        cursor.execute(data_query, params)
        results = cursor.fetchall()

        self.table.setRowCount(len(results))
        for i, (timestamp, database, query) in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.table.setItem(i, 1, QTableWidgetItem(database))
            self.table.setItem(i, 2, QTableWidgetItem(query))
            
            reuse_btn = QPushButton("Reuse")
            reuse_btn.clicked.connect(lambda _, q=query: self.reuse_query(q))
            self.table.setCellWidget(i, 3, reuse_btn)

        self.update_pagination_controls()

    def update_pagination_controls(self):
        self.page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_page()

    def reuse_query(self, query):
        self.parent().query_input.setPlainText(query)
        self.accept()
def main():
    app = QApplication(sys.argv)
    StyleHelper.set_dark_theme(app)
    ex = DatabaseApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()