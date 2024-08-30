from PyQt5.QtGui import QColor, QPalette
from datetime import datetime, timedelta


import sys
import psycopg2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, 
                             QComboBox, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QSpinBox,
                             QStackedWidget, QDoubleSpinBox)
from PyQt5.QtCore import Qt

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.person_id_input = QLineEdit()
        self.person_id_input.setPlaceholderText("Enter Person ID")
        layout.addWidget(self.person_id_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Connect to database
        self.conn = psycopg2.connect(
            dbname="Project",
            user="nanda",
            password="nanda",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()

    def login(self):
        person_id = self.person_id_input.text()
        password = self.password_input.text()

        # Check customer table
        self.cursor.execute("SELECT * FROM customer WHERE person_id = %s AND password = %s", (person_id, password))
        customer = self.cursor.fetchone()

        # Check supplier table
        self.cursor.execute("SELECT * FROM supplier WHERE person_id = %s AND password = %s", (person_id, password))
        supplier = self.cursor.fetchone()

        if customer:
            self.status_label.setText(f"Logged in as Customer (ID: {customer[0]})")
            self.show_customer_interface(customer[0])
        elif supplier:
            self.status_label.setText(f"Logged in as Supplier (ID: {supplier[0]})")
            self.show_supplier_interface(supplier[0])
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials")

    def show_customer_interface(self, customer_id):
        self.customer_interface = CustomerInterface(self.conn, customer_id)
        self.customer_interface.show()
        self.hide()

    def show_supplier_interface(self, supplier_id):
        self.supplier_interface = SupplierInterface(self.conn, supplier_id)
        self.supplier_interface.show()
        self.hide()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

class CustomerInterface(QMainWindow):
    def __init__(self, conn, customer_id):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.customer_id = customer_id

        # Fetch customer name
        self.cursor.execute("""
            SELECT p.name
            FROM customer c
            JOIN person p ON c.person_id = p.person_id
            WHERE c.customer_id = %s
        """, (self.customer_id,))
        customer_name = self.cursor.fetchone()[0]

        self.setWindowTitle(f"Welcome {customer_name}")
        self.setGeometry(100, 100, 800, 600)

        # Set color scheme
        self.set_color_scheme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        # View Products
        view_products_button = QPushButton("View Products")
        view_products_button.setStyleSheet(button_style)
        view_products_button.clicked.connect(self.view_products)
        layout.addWidget(view_products_button)

        # Order New Products
        order_button = QPushButton("Order New Products")
        order_button.setStyleSheet(button_style)
        order_button.clicked.connect(self.order_products)
        layout.addWidget(order_button)

        # View Recent Orders
        view_orders_button = QPushButton("View Recent Orders")
        view_orders_button.setStyleSheet(button_style)
        view_orders_button.clicked.connect(self.view_recent_orders)
        layout.addWidget(view_orders_button)

        

        # Check Order Status
        check_status_button = QPushButton("Check Order Status")
        check_status_button.setStyleSheet(button_style)
        check_status_button.clicked.connect(self.check_order_status)
        layout.addWidget(check_status_button)

        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create pages
        self.table_page = QWidget()
        self.table_layout = QVBoxLayout(self.table_page)
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #f0f8ff;
                alternate-background-color: #e6f3ff;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: 1px solid #ddd;
            }
        """)
        self.table_layout.addWidget(self.table_widget)

        self.order_page = QWidget()
        self.order_layout = QVBoxLayout(self.order_page)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.table_page)
        self.stacked_widget.addWidget(self.order_page)

    def set_color_scheme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#E6F3FF"))  # Light blue background
        palette.setColor(QPalette.WindowText, QColor("#333333"))  # Dark grey text
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))  # White base
        palette.setColor(QPalette.AlternateBase, QColor("#F0F8FF"))  # Alternate light blue
        palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ToolTipText, QColor("#333333"))
        palette.setColor(QPalette.Text, QColor("#333333"))
        palette.setColor(QPalette.Button, QColor("#4CAF50"))  # Green buttons
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.BrightText, QColor("#FF0000"))
        palette.setColor(QPalette.Highlight, QColor("#4CAF50").lighter())
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #E6F3FF, stop:1 #FFFFFF);
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
            }
        """)

    def view_products(self):
        self.cursor.execute("""
            SELECT p.product_id, p.product_name, i.quantity, p.price
            FROM product p
            JOIN inventory i ON p.product_id = i.product_id
        """)
        self.display_table_data(self.cursor.fetchall(), ['Product ID', 'Product Name', 'Quantity', 'Price'])
        self.stacked_widget.setCurrentWidget(self.table_page)

    def order_products(self):
        # Clear existing widgets
        for i in reversed(range(self.order_layout.count())): 
            self.order_layout.itemAt(i).widget().setParent(None)

        self.cursor.execute("SELECT product_id, product_name FROM product")
        products = self.cursor.fetchall()
        
        self.product_combo = QComboBox()
        self.product_combo.addItems([f"{p[0]} - {p[1]}" for p in products])
        self.order_layout.addWidget(self.product_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.order_layout.addWidget(self.quantity_spin)
        
        confirm_button = QPushButton("Confirm Order")
        confirm_button.clicked.connect(self.confirm_order)
        self.order_layout.addWidget(confirm_button)
        
        self.stacked_widget.setCurrentWidget(self.order_page)

    def confirm_order(self):
        product_id = self.product_combo.currentText().split(' - ')[0]
        quantity = self.quantity_spin.value()
        
        try:
            self.cursor.execute("BEGIN")
            
            self.cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (product_id,))
            current_quantity = self.cursor.fetchone()[0]
            
            if current_quantity < quantity:
                raise Exception(f"Not enough inventory. Available: {current_quantity}")
            
            # Create a new order
            self.cursor.execute("""
                INSERT INTO sales_order (customer_id, order_date, status_id) 
                VALUES (%s, CURRENT_DATE, 1) 
                RETURNING order_id
            """, (self.customer_id,))
            order_id = self.cursor.fetchone()[0]
            
            # Add order details
            self.cursor.execute("""
                INSERT INTO order_details (order_details_id, order_id, product_id, supplier_id) 
                SELECT 
                    CONCAT('OD', COALESCE(MAX(SUBSTRING(od.order_details_id FROM 3)::integer), 0) + 1), 
                    %s, 
                    %s, 
                    ps.supplier_id
                FROM 
                    order_details od, 
                    product_supplier ps 
                WHERE 
                    ps.product_id = %s 
                GROUP BY 
                    ps.supplier_id       
            """, (order_id, product_id, product_id))
            
            # Update inventory
            self.cursor.execute("""
                UPDATE inventory
                SET quantity = quantity - %s
                WHERE product_id = %s
            """, (quantity, product_id))
            
            # Generate and insert confirmation message
            self.cursor.execute("""
                INSERT INTO confirm_msg (order_id, message_text)
                SELECT so.order_id, CONCAT(
                    'Dear ', p.name, ', your order with order ID ', so.order_id, 
                    ' for ', %s, ' units of product ', %s,
                    ' has been placed successfully on ', so.order_date, 
                    '. Thank you for shopping with us.'
                ) AS message_text
                FROM sales_order so
                JOIN customer c ON so.customer_id = c.customer_id
                JOIN person p ON c.person_id = p.person_id
                WHERE so.order_id = %s
                RETURNING message_text, sent_at
            """, (quantity, product_id, order_id))
            
            confirmation_result = self.cursor.fetchone()
            confirmation_message = confirmation_result[0]
            sent_at = confirmation_result[1]
            
            # Commit the transaction
            self.conn.commit()
            
            QMessageBox.information(self, "Order Confirmation", 
                                    f"{confirmation_message}\n\nSent at: {sent_at}")
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

        # Refresh the product view
        self.view_products()
        self.stacked_widget.setCurrentWidget(self.table_page)

    def view_recent_orders(self):
        current_time = datetime.now()
        self.cursor.execute("""
            SELECT so.order_id, so.order_date, p.product_name, od.supplier_id,
                   CASE 
                       WHEN %s::timestamp - so.order_date::timestamp < INTERVAL '5 hours' THEN 'Order Placed'
                       WHEN %s::timestamp - so.order_date::timestamp < INTERVAL '7 hours' THEN 'Shipped'
                       ELSE 'Delivered'
                   END as status
            FROM sales_order so
            JOIN order_details od ON so.order_id = od.order_id
            JOIN product p ON od.product_id = p.product_id
            WHERE so.customer_id = %s
            ORDER BY so.order_date DESC
            LIMIT 10
        """, (current_time, current_time, self.customer_id))
        self.display_table_data(self.cursor.fetchall(), ['Order ID', 'Order Date', 'Product', 'Supplier ID', 'Status'])
        self.stacked_widget.setCurrentWidget(self.table_page)

    def check_order_status(self):
        current_time = datetime.now()
        self.cursor.execute("""
            SELECT so.order_id, so.order_date,
                   CASE 
                       WHEN %s::timestamp - so.order_date::timestamp < INTERVAL '5 hours' THEN 'Order Placed'
                       WHEN %s::timestamp - so.order_date::timestamp < INTERVAL '7 hours' THEN 'Shipped'
                       ELSE 'Delivered'
                   END as status
            FROM sales_order so
            WHERE so.customer_id = %s
            ORDER BY so.order_date DESC
        """, (current_time, current_time, self.customer_id))
        self.display_table_data(self.cursor.fetchall(), ['Order ID', 'Order Date', 'Status'])
        self.stacked_widget.setCurrentWidget(self.table_page)


    def display_table_data(self, data, headers):
        self.table_widget.clear()
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(cell_data)))

        self.table_widget.resizeColumnsToContents()


class SupplierInterface(QMainWindow):
    def __init__(self, conn, supplier_id):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.supplier_id = supplier_id
        self.cursor.execute("""
            SELECT p.name
            FROM supplier s
            JOIN person p ON s.person_id = p.person_id
            WHERE s.supplier_id = %s
        """, (self.supplier_id,))
        supplier_name = self.cursor.fetchone()[0]

        # Set window title with welcome message
        self.setWindowTitle(f"Welcome {supplier_name}")
        self.setGeometry(100, 100, 800, 600)

        # Set color scheme
        self.set_color_scheme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        update_inventory_button = QPushButton("Update Inventory")
        update_inventory_button.setStyleSheet(button_style)
        update_inventory_button.clicked.connect(self.update_inventory)
        layout.addWidget(update_inventory_button)

        view_inventory_button = QPushButton("View Inventory")
        view_inventory_button.setStyleSheet(button_style)
        view_inventory_button.clicked.connect(self.view_inventory)
        layout.addWidget(view_inventory_button)

        add_product_button = QPushButton("Add New Product")
        add_product_button.setStyleSheet(button_style)
        add_product_button.clicked.connect(self.add_new_product)
        layout.addWidget(add_product_button)

        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create pages
        self.table_page = QWidget()
        self.table_layout = QVBoxLayout(self.table_page)
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #f0f8ff;
                alternate-background-color: #e6f3ff;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: 1px solid #ddd;
            }
        """)
        self.table_layout.addWidget(self.table_widget)

        self.update_page = QWidget()
        self.update_layout = QVBoxLayout(self.update_page)

        self.add_product_page = QWidget()
        self.add_product_layout = QVBoxLayout(self.add_product_page)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.table_page)
        self.stacked_widget.addWidget(self.update_page)
        self.stacked_widget.addWidget(self.add_product_page)

    def set_color_scheme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#E6F3FF"))  # Light blue background
        palette.setColor(QPalette.WindowText, QColor("#333333"))  # Dark grey text
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))  # White base
        palette.setColor(QPalette.AlternateBase, QColor("#F0F8FF"))  # Alternate light blue
        palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ToolTipText, QColor("#333333"))
        palette.setColor(QPalette.Text, QColor("#333333"))
        palette.setColor(QPalette.Button, QColor("#4CAF50"))  # Green buttons
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.BrightText, QColor("#FF0000"))
        palette.setColor(QPalette.Highlight, QColor("#4CAF50").lighter())
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 #E6F3FF, stop:1 #FFFFFF);
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
            }
        """)

    def update_inventory(self):
        # Clear existing widgets
        for i in reversed(range(self.update_layout.count())): 
            self.update_layout.itemAt(i).widget().setParent(None)

        self.cursor.execute("""
            SELECT p.product_id, p.product_name, i.quantity, p.price
            FROM product p
            JOIN inventory i ON p.product_id = i.product_id
            JOIN product_supplier ps ON p.product_id = ps.product_id
            WHERE ps.supplier_id = %s
        """, (self.supplier_id,))
        products = self.cursor.fetchall()

        self.product_combos = []
        self.quantity_spins = []
        self.price_spins = []

        for product in products:
            product_layout = QHBoxLayout()
            product_combo = QComboBox()
            product_combo.addItem(f"{product[0]} - {product[1]}")
            product_layout.addWidget(product_combo)
            
            quantity_spin = QSpinBox()
            quantity_spin.setRange(-1000, 1000)  # Allow negative values for stock reduction
            quantity_spin.setValue(0)
            product_layout.addWidget(quantity_spin)
            
            price_spin = QDoubleSpinBox()
            price_spin.setRange(0.01, 10000.00)
            price_spin.setValue(product[3])
            product_layout.addWidget(price_spin)
            
            self.update_layout.addLayout(product_layout)
            
            self.product_combos.append(product_combo)
            self.quantity_spins.append(quantity_spin)
            self.price_spins.append(price_spin)

        confirm_button = QPushButton("Confirm Update")
        confirm_button.clicked.connect(self.confirm_update)
        self.update_layout.addWidget(confirm_button)

        self.stacked_widget.setCurrentWidget(self.update_page)

    def confirm_update(self):
        try:
            for combo, spin, price_spin in zip(self.product_combos, self.quantity_spins, self.price_spins):
                product_id = combo.currentText().split(' - ')[0]
                quantity_change = spin.value()
                new_price = price_spin.value()
                
                if quantity_change != 0:
                    self.cursor.execute("""
                        UPDATE inventory
                        SET quantity = quantity + %s
                        WHERE product_id = %s
                    """, (quantity_change, product_id))
                
                self.cursor.execute("""
                    UPDATE product
                    SET price = %s
                    WHERE product_id = %s
                """, (new_price, product_id))

            self.conn.commit()
            QMessageBox.information(self, "Inventory Updated", "Inventory and product information have been updated successfully.")
            self.view_inventory()
            self.stacked_widget.setCurrentWidget(self.table_page)

        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", f"An error occurred while updating: {str(e)}")

    def view_inventory(self):
        self.cursor.execute("""
            SELECT p.product_id, p.product_name, i.quantity, p.price
            FROM product p
            JOIN inventory i ON p.product_id = i.product_id
            JOIN product_supplier ps ON p.product_id = ps.product_id
            WHERE ps.supplier_id = %s
        """, (self.supplier_id,))
        self.display_table_data(self.cursor.fetchall(), ['Product ID', 'Product Name', 'Quantity', 'Price'])
        self.stacked_widget.setCurrentWidget(self.table_page)
    
    def add_new_product(self):
    # Clear existing widgets
        for i in reversed(range(self.add_product_layout.count())): 
            self.add_product_layout.itemAt(i).widget().setParent(None)

        # Create input fields
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Enter Product Name")
        self.add_product_layout.addWidget(self.product_name_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 10000.00)
        self.price_input.setPrefix("$")
        self.add_product_layout.addWidget(self.price_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000)
        self.add_product_layout.addWidget(self.quantity_input)

        confirm_button = QPushButton("Add Product")
        confirm_button.clicked.connect(self.confirm_add_product)
        self.add_product_layout.addWidget(confirm_button)

        self.stacked_widget.setCurrentWidget(self.add_product_page)
    
    def confirm_add_product(self):
        product_name = self.product_name_input.text()
        price = self.price_input.value()
        quantity = self.quantity_input.value()

        try:
            self.cursor.execute("BEGIN")
            
            # Get the next value from the sequence
            self.cursor.execute("SELECT nextval('product_product_id_seq')")
            next_id = self.cursor.fetchone()[0]
            
            # Generate the new product_id in 'P#' format
            new_id = f'P{next_id}'
            
            # Insert new product
            self.cursor.execute("""
                INSERT INTO product (product_id, product_name, price)
                VALUES (%s, %s, %s)
            """, (new_id, product_name, price))

            # Add to inventory
            self.cursor.execute("""
                INSERT INTO inventory (product_id, quantity)
                VALUES (%s, %s)
            """, (new_id, quantity))

            # Link product to supplier
            self.cursor.execute("""
                INSERT INTO product_supplier (product_id, supplier_id)
                VALUES (%s, %s)
            """, (new_id, self.supplier_id))

            self.conn.commit()
            QMessageBox.information(self, "Success", f"New product added successfully with ID: {new_id}")
            self.view_inventory()
            self.stacked_widget.setCurrentWidget(self.table_page)

        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", f"An error occurred while adding the product: {str(e)}")

    def display_table_data(self, data, headers):
        self.table_widget.clear()
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(cell_data)))

        self.table_widget.resizeColumnsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())