import mplcursors  # Importing mplcursors for hover functionality
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from plyer import notification
import csv
import os

# Function to scrape real-time exchange rate


def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"https://www.x-rates.com/calculator/?from={
            from_currency}&to={to_currency}&amount=1"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the exchange rate in the HTML
        rate_value = soup.find("span", class_="ccOutputRslt")
        if rate_value:
            # Clean and parse the rate
            raw_rate = rate_value.text.strip()  # Remove any extra spaces
            # Keep only numbers and dots
            clean_rate = "".join(
                [c for c in raw_rate if c.isdigit() or c == "."])
            return float(clean_rate)  # Convert to float
        else:
            raise ValueError("Exchange rate not found on the webpage.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch exchange rate: {e}")
        return None

# Save conversion history to a CSV file


def save_conversion_to_history(base_currency, target_currency, amount, result):
    file_name = "conversion_history.csv"
    header = ["Base Currency", "Target Currency", "Amount", "Result"]

    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow([base_currency, target_currency, amount, result])

# Periodically check exchange rates for notifications


def monitor_exchange_rate(base_currency, target_currency, threshold):
    def check_rate():
        last_rate = get_exchange_rate(base_currency, target_currency)
        while True:
            time.sleep(60)  # Check every 60 seconds
            current_rate = get_exchange_rate(base_currency, target_currency)
            if current_rate is None:
                continue
            if abs(current_rate - last_rate) >= threshold:
                notification.notify(
                    title="Exchange Rate Alert!",
                    message=f"{base_currency} to {target_currency} rate changed: {
                        last_rate:.2f} -> {current_rate:.2f}",
                    timeout=10
                )
                last_rate = current_rate

    thread = threading.Thread(target=check_rate, daemon=True)
    thread.start()

# Function to plot comparison graph


def plot_graph(base_currency, amount, rates, converter_window):
    currencies = list(rates.keys())
    values = [amount * rate for rate in rates.values()]

    figure, ax = plt.subplots(figsize=(8, 5), dpi=100)
    bars = ax.bar(currencies, values, color="skyblue")

    # Configure graph appearance
    ax.set_title(f"Comparison of {amount} {
                 base_currency} with Other Currencies", fontsize=14)
    ax.set_xlabel("Currencies", fontsize=12)
    ax.set_ylabel("Equivalent Amount", fontsize=12)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5)

    # Add hover functionality
    # Enable hover effect on the bars
    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f"{currencies[sel.index]}: {values[sel.index]:.2f}")
    )

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(figure, converter_window)
    canvas.get_tk_widget().pack(pady=20)
    canvas.draw()


# Function to open conversion history


def open_history():
    history_window = tk.Toplevel()
    history_window.title("Conversion History")
    history_window.geometry("600x400")

    file_name = "conversion_history.csv"
    if os.path.isfile(file_name):
        with open(file_name, mode="r") as file:
            reader = csv.reader(file)
            history_text = tk.Text(
                history_window, wrap="word", font=("Helvetica", 12))
            history_text.pack(expand=True, fill="both")
            for row in reader:
                history_text.insert(tk.END, "\t".join(row) + "\n")
    else:
        tk.Label(history_window, text="No history found!",
                 font=("Helvetica", 14)).pack()

# Function to open the currency converter


def open_currency_converter():
    converter_window = tk.Tk()
    converter_window.title("Currency Converter with Notifications")
    converter_window.geometry("800x600")

    bg_image = Image.open("bg.jpeg").resize(
        (1920, 1080), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(converter_window, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)

    currencies = ["USD - United States Dollar", "EUR - Euro", "GBP - British Pound", "INR - Indian Rupee",
                  "JPY - Japanese Yen", "AUD - Australian Dollar", "CAD - Canadian Dollar", "CHF - Swiss Franc",
                  "CNY - Chinese Yuan", "NZD - New Zealand Dollar"]

    def get_currency_code(selection):
        return selection.split(" - ")[0]

    header = tk.Label(converter_window, text="Currency Converter", font=(
        "Helvetica", 24, "bold"), bg="#f0f8ff", fg="black")
    header.pack(pady=20)

    from_currency_label = tk.Label(
        converter_window, text="From Currency:", font=("Helvetica", 12), bg="#f0f8ff")
    from_currency_label.pack(pady=5)
    from_currency_dropdown = ttk.Combobox(
        converter_window, values=currencies, state="readonly", width=40)
    from_currency_dropdown.pack()
    from_currency_dropdown.current(0)

    to_currency_label = tk.Label(
        converter_window, text="To Currency:", font=("Helvetica", 12), bg="#f0f8ff")
    to_currency_label.pack(pady=10)
    to_currency_dropdown = ttk.Combobox(
        converter_window, values=currencies, state="readonly", width=40)
    to_currency_dropdown.pack()
    to_currency_dropdown.current(1)

    amount_label = tk.Label(converter_window, text="Amount:",
                            font=("Helvetica", 12), bg="#f0f8ff")
    amount_label.pack(pady=10)
    amount_entry = tk.Entry(converter_window, width=30)
    amount_entry.pack()

    result_label = tk.Label(converter_window, text="", font=(
        "Helvetica", 14, "bold"), fg="#006400", bg="#f0f8ff")
    result_label.pack(pady=20)

    def convert_currency():
        from_currency_code = get_currency_code(from_currency_dropdown.get())
        to_currency_code = get_currency_code(to_currency_dropdown.get())
        amount = amount_entry.get()

        try:
            amount = float(amount)
            rate = get_exchange_rate(from_currency_code, to_currency_code)
            if rate:
                result = amount * rate
                result_label.config(
                    text=f"{amount} {from_currency_code} = {
                        result:.2f} {to_currency_code}"
                )
                save_conversion_to_history(
                    from_currency_code, to_currency_code, amount, result)

                rates = {get_currency_code(currency): get_exchange_rate(from_currency_code, get_currency_code(currency))
                         for currency in currencies if get_currency_code(currency) != from_currency_code}

                plot_graph(from_currency_code, amount, rates, converter_window)
            else:
                result_label.config(text="Conversion failed. Try again.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    convert_button = tk.Button(converter_window, text="Convert", font=("Helvetica", 12, "bold"), bg="gold", fg="black",
                               command=convert_currency)
    convert_button.pack(pady=10)

    history_button = tk.Button(converter_window, text="View History", font=(
        "Helvetica", 12), bg="lightblue", command=open_history)
    history_button.pack(pady=10)

    converter_window.mainloop()

# Login Page


def unlock_vault():
    username = username_entry.get()
    combination = combination_entry.get()

    if username == "Infotact" and combination == "1234":
        messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
        login_window.destroy()
        open_currency_converter()
    else:
        messagebox.showerror(
            "Access Denied", "Invalid combination or username! Try again.")


# Main Login Window
login_window = tk.Tk()
login_window.title("Login to Currency Vault")
login_window.geometry("1920x1080")

bg_image = Image.open("bg.jpeg").resize((1920, 1080), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(login_window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

header = tk.Label(login_window, text="🔒 Secure Currency Vault Login", font=(
    "Helvetica", 18, "bold"), bg="#f0f8ff", fg="black")
header.pack(pady=20)

username_label = tk.Label(login_window, text="Username:", font=(
    "Helvetica", 12), bg="#f0f8ff", fg="black")
username_label.pack(pady=10)
username_entry = tk.Entry(login_window, width=30, font=("Helvetica", 12))
username_entry.pack()

combination_label = tk.Label(login_window, text="Vault Combination (4-digit code):",
                             font=("Helvetica", 12), bg="#f0f8ff", fg="black")
combination_label.pack(pady=10)
combination_entry = tk.Entry(
    login_window, width=10, font=("Helvetica", 12), show="*")
combination_entry.pack()

unlock_button = tk.Button(login_window, text="Unlock Vault", font=(
    "Helvetica", 12, "bold"), bg="gold", fg="black", command=unlock_vault)
unlock_button.pack(pady=20)

login_window.mainloop()
