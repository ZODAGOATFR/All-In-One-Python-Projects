from textblob import TextBlob

while True:
    a = input("Enter the word to be checked: ")
    print(f"Original text: {a}")

    b = TextBlob(a)
    print(f"Corrected text: {b.correct()}")

    choice = input("Try Again? (y/n): ").strip().lower()
    if choice != "y":
        print("Goodbye!")
        break
