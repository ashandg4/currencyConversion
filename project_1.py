import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to scrape real-time exchange rate


def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"https://www.x-rates.com/calculator/?from={
            from_currency}&to={to_currency}&amount=1"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Inspect the updated website structure for the correct class or id
        rate_element = soup.find("span", class_="ccOutputTrail")
        if rate_element:
            rate = rate_element.previous_sibling.text + rate_element.text
            return float(rate.replace(",", ""))
        else:
            raise ValueError("Exchange rate not found on the webpage.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch exchange rate: {e}")
        return None


# Function to plot comparison graph


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

    # Add a tooltip for hover functionality
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
        fontsize=10,
        color="black",
    )
    annot.set_visible(False)

    def update_annot(bar):
        """Update the annotation to display value."""
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        annot.xy = (x, y)
        text = f"{currencies[bars.index(bar)]}: {y:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        """Handle hover event over bars."""
        visible = annot.get_visible()
        if event.inaxes == ax:
            for bar in bars:
                if bar.contains(event)[0]:
                    update_annot(bar)
                    annot.set_visible(True)
                    figure.canvas.draw_idle()
                    return
        if visible:
            annot.set_visible(False)
            figure.canvas.draw_idle()

    # Connect the hover event to the graph
    figure.canvas.mpl_connect("motion_notify_event", hover)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(figure, converter_window)
    canvas.get_tk_widget().pack(pady=20)
    canvas.draw()


# Function to open the currency converter


def open_currency_converter():
    converter_window = tk.Tk()
    converter_window.title("Currency Converter with Background Image")
    converter_window.geometry("800x600")

    # Add a background image
    bg_image = Image.open("bg.jpeg")
    bg_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(converter_window, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)  # Full window background

    # Predefined list of currencies
    currencies = [
        "USD - United States Dollar",
        "EUR - Euro",
        "GBP - British Pound",
        "INR - Indian Rupee",
        "JPY - Japanese Yen",
        "AUD - Australian Dollar",
        "CAD - Canadian Dollar",
        "CHF - Swiss Franc",
        "CNY - Chinese Yuan",
        "NZD - New Zealand Dollar",
    ]

    def get_currency_code(selection):
        return selection.split(" - ")[0]

    # Header
    header = tk.Label(
        converter_window,
        text="Currency Converter",
        font=("Helvetica", 24, "bold"),
        bg="#f0f8ff",
        fg="black",
    )
    header.pack(pady=20)

    # From Currency
    from_currency_label = tk.Label(
        converter_window, text="From Currency:", font=("Helvetica", 12), bg="#f0f8ff"
    )
    from_currency_label.pack(pady=5)
    from_currency_dropdown = ttk.Combobox(
        converter_window, values=currencies, state="readonly", width=40
    )
    from_currency_dropdown.pack()
    from_currency_dropdown.current(0)

    # To Currency
    to_currency_label = tk.Label(
        converter_window, text="To Currency:", font=("Helvetica", 12), bg="#f0f8ff"
    )
    to_currency_label.pack(pady=10)
    to_currency_dropdown = ttk.Combobox(
        converter_window, values=currencies, state="readonly", width=40
    )
    to_currency_dropdown.pack()
    to_currency_dropdown.current(1)

    # Amount Entry
    amount_label = tk.Label(
        converter_window, text="Amount:", font=("Helvetica", 12), bg="#f0f8ff"
    )
    amount_label.pack(pady=10)
    amount_entry = tk.Entry(converter_window, width=30)
    amount_entry.pack()

    # Conversion Result
    result_label = tk.Label(
        converter_window, text="", font=("Helvetica", 14, "bold"), fg="#006400", bg="#f0f8ff"
    )
    result_label.pack(pady=20)

    # Function to convert currency
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

                # Prepare rates for multiple currencies
                rates = {}
                for currency in currencies:
                    currency_code = get_currency_code(currency)
                    if currency_code != from_currency_code:
                        rates[currency_code] = get_exchange_rate(
                            from_currency_code, currency_code)

                # Plot the graph
                plot_graph(from_currency_code, amount, rates, converter_window)
            else:
                result_label.config(text="Conversion failed. Try again.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    # Convert Button
    convert_button = tk.Button(
        converter_window,
        text="Convert",
        font=("Helvetica", 12, "bold"),
        bg="gold",
        fg="black",
        command=convert_currency,
    )
    convert_button.pack(pady=10)

    # Run the converter window
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

# Add a background image
bg_image = Image.open("bg.jpeg")
bg_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(login_window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)  # Full window background

# Header
header = tk.Label(
    login_window,
    text="🔒 Secure Currency Vault Login",
    font=("Helvetica", 18, "bold"),
    bg="#f0f8ff",
    fg="black",
)
header.pack(pady=20)

# Username Entry
username_label = tk.Label(
    login_window, text="Username:", font=("Helvetica", 12), bg="#f0f8ff", fg="black"
)
username_label.pack(pady=10)
username_entry = tk.Entry(login_window, width=30, font=("Helvetica", 12))
username_entry.pack()

# Combination Entry
combination_label = tk.Label(
    login_window,
    text="Vault Combination (4-digit code):",
    font=("Helvetica", 12),
    bg="#f0f8ff",
    fg="black",
)
combination_label.pack(pady=10)
combination_entry = tk.Entry(
    login_window, width=10, font=("Helvetica", 12), show="*"
)
combination_entry.pack()

# Unlock Button
unlock_button = tk.Button(
    login_window,
    text="Unlock Vault",
    font=("Helvetica", 12, "bold"),
    bg="gold",
    fg="black",
    command=unlock_vault,
)
unlock_button.pack(pady=20)

# Run the login window
login_window.mainloop()
