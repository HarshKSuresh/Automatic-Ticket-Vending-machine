import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import random
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import requests

class BusTicketBookingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Ticket Booking")
        self.root.geometry("600x400")
        self.root.configure(bg="#E8E8E8")  # Set background color

        self.all_places = [
            "Kempegowda Bus Station/Majestic", "Anand Rao Circle", "Race Course Road",
            "Sivananda Stores", "Bangalore Golf Course", "Windsor Manor", "Palace Guttahalli",
            "Cauvery Theater", "Palace Grounds", "Mekhri Circle", "Iaf Training School",
            "Ganganagar", "Cbi", "Veterinary College", "Hebbal Canara Bank", "Hebbal"
        ]

        self.create_welcome_page()

    def create_welcome_page(self):
        self.clear_window()

        # Welcome Label
        welcome_label = tk.Label(
            self.root, text="Welcome to Bus Ticket Booking", font=("Arial", 24, "bold"),
            bg="#E8E8E8", fg="#333333"
        )
        welcome_label.pack(pady=40)

        # Start Button
        start_button = tk.Button(
            self.root, text="Start Booking", font=("Arial", 14), bg="#33A1C9", fg="#FFFFFF",
            command=self.create_booking_page
        )
        start_button.pack()

    def create_booking_page(self):
        self.clear_window()

        # From Label and Entry
        from_label = tk.Label(
            self.root, text="From:", font=("Arial", 16, "bold"), bg="#E8E8E8", fg="#333333"
        )
        from_label.pack()
        self.from_var = tk.StringVar()
        self.from_combobox = ttk.Combobox(
            self.root, textvariable=self.from_var, font=("Arial", 14), state="readonly"
        )
        self.from_combobox.pack(pady=5)
        self.from_combobox.set("Select From")
        self.from_combobox['values'] = self.all_places

        # To Label and Entry
        to_label = tk.Label(
            self.root, text="To:", font=("Arial", 16, "bold"), bg="#E8E8E8", fg="#333333"
        )
        to_label.pack()
        self.to_var = tk.StringVar()
        self.to_combobox = ttk.Combobox(
            self.root, textvariable=self.to_var, font=("Arial", 14), state="readonly"
        )
        self.to_combobox.pack(pady=5)
        self.to_combobox.set("Select To")

        # Submit Button
        submit_button = tk.Button(
            self.root, text="Submit", font=("Arial", 14), bg="#33A1C9", fg="#FFFFFF",
            command=self.generate_ticket
        )
        submit_button.pack(pady=20)

        # Bind the selection change event of the From combobox to update the To combobox options
        self.from_combobox.bind("<<ComboboxSelected>>", self.update_to_options)

    def update_to_options(self, *args):
        from_place = self.from_var.get()
        selected_index = self.all_places.index(from_place)
        to_values = self.all_places[selected_index + 1:]
        self.to_combobox['values'] = to_values

    def generate_ticket(self):
        from_place = self.from_var.get()
        to_place = self.to_var.get()
    
        if from_place and to_place:
            from_price = self.get_stop_price(from_place)
            to_price = self.get_stop_price(to_place)
            
            ticket_price = abs(to_price - from_price)
            
            # makethe ticket price to 2 decimal places
            ticket_price = "{:.2f}".format(ticket_price)
            
            current_datetime = datetime.now()
            formatted_date = current_datetime.strftime("%d-%m-%Y")
            formatted_time = current_datetime.strftime("%I:%M %p")
    
            # Generate random ticket number
            ticket_number = random.randint(10000, 99999)
    
            ticket_info = f"{'BMTC':^30}\n\n"
            ticket_info += f"{'Date:':<10} {formatted_date:>20}\n"
            ticket_info += f"{'Time:':<10} {formatted_time:>20}\n"
            ticket_info += f"{'Ticket No:':<10} {ticket_number:>20}\n"
            ticket_info += f"{'Bus Number:':<10} {'BMTC-287':>20}\n\n"
            ticket_info += f"{from_place}\n"
            ticket_info += f"{'TO':^30}\n"
            ticket_info += f"{to_place}\n\n"
            ticket_info += f"{'Total Fare:':<10} {ticket_price:>10} Rs."
    
            dialog = tk.Toplevel(self.root)
            dialog.title("Ticket Information")
    
            ticket_label = tk.Label(
                dialog, text=ticket_info, font=("Arial", 12), bg="#E8E8E8", fg="#333333", justify="center"
            )
            ticket_label.pack(padx=10, pady=10)
    
            qr_code_path = self.generate_gpay_qr_code(ticket_price)
    
            if os.path.exists(qr_code_path):
                qr_code_image = tk.PhotoImage(file=qr_code_path)
                qr_code_label = tk.Label(dialog, image=qr_code_image, bg="#E8E8E8")
                qr_code_label.image = qr_code_image
                qr_code_label.pack(pady=10)
    
            def process_payment():
                payment_status = messagebox.askyesno("Payment", "Has the payment been completed?")
                if payment_status:
                    self.print_ticket(ticket_info)
                else:
                    messagebox.showwarning("Payment Incomplete", "Please complete the payment.")
    
            process_button = tk.Button(
                dialog, text="Process Payment", font=("Arial", 12), bg="#33A1C9", fg="#FFFFFF",
                command=process_payment
            )
            process_button.pack(pady=10)
    
            close_button = tk.Button(
                dialog, text="Close", font=("Arial", 12), bg="#33A1C9", fg="#FFFFFF",
                command=dialog.destroy
            )
            close_button.pack(pady=10)
        else:
            messagebox.showerror("Error", "Please select both 'From' and 'To' places.")
    
    def get_stop_price(self, stop):
        stop_prices = {
            "Kempegowda Bus Station/Majestic": 0,
            "Anand Rao Circle": 5,
            "Race Course Road": 8,
            "Sivananda Stores": 12,
            "Bangalore Golf Course": 15,
            "Windsor Manor": 18,
            "Palace Guttahalli": 20,
            "Cauvery Theater": 24,
            "Palace Grounds": 28,
            "Mekhri Circle": 32,
            "Iaf Training School": 36,
            "Ganganagar": 40,
            "Cbi": 43,
            "Veterinary College": 48,
            "Hebbal Canara Bank": 52,
            "Hebbal": 55
        }
        return stop_prices.get(stop, 0)

    def generate_gpay_qr_code(self, amount):
        qr_code_path = 'payment_qr_code.png'

        url = f"https://upiqr.in/api/qr?name=Harsh K Suresh&vpa=harshksuresh0030@oksbi&amount={amount}&format=png"
        response = requests.get(url)

        if response.status_code == 200:
            with open(qr_code_path, 'wb') as f:
                f.write(response.content)
                
            # print('QR code saved successfully!')
        # else:
        #     print('Failed to generate QR code.')

        return qr_code_path
           
    def print_ticket(self, ticket_info):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            c = canvas.Canvas(save_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 12)

        # Add the image to the PDF
            image_path = "C:/Users/Windows 11/Downloads/BMTC_Logo.png"  # Replace with the actual image path
            img = Image.open(image_path)
            x = 175  # Define the x-coordinate
            y = 510  # Define the y-coordinate
            c.drawInlineImage(img, x, y, width=250, height=250)  # Adjust the coordinates and size as needed

            text_lines = ticket_info.split("\n")
            y = 750
            for line in text_lines:
                c.drawCentredString(300, y, line)
                y -= 20

            c.showPage()
            c.save()
            messagebox.showinfo("Ticket Printed", "Ticket has been saved as a PDF file.")
        else:
            messagebox.showwarning("Invalid File Name", "Please provide a valid file name to save the ticket.")
            
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


root = tk.Tk()
ticket_booking_gui = BusTicketBookingGUI(root)
root.mainloop()