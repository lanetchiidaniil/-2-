"""Application entry point."""
import tkinter as tk

from tsquare_app import TSquareApp


def main():
    root = tk.Tk()
    TSquareApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
