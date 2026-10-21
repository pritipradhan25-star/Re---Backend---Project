
from flask import Flask, request, jsonify, render_template
from pathlib import Path

app = Flask(__name__)

STOCK_FILE = Path(__file__).with_name("ingredients.txt")

pizza_ingredients = {
    "veg": {"onion": 1, "tomato": 2, "chese": 1},
    "paneer": {
        "onion": 1, "tomato": 1, "chese": 1, "paneer": 2
    },
    "chese": {"chese": 1, "tomato": 3, "onion": 2}
}

burger_ingredients = {
    "veg": {"onion": 1, "tomato": 2, "bred": 2},
    "nonveg": {
        "onion": 1, "tomato": 2, "chiken": 1, "bred": 2
    },
    "chese": {"bred": 2, "chese": 1, "tomato": 3, "onion": 2}
}


def read_ingredients():
    stock = {}
    with STOCK_FILE.open("r") as file:
        for line in file:
            name, quantity = line.strip().split(":")
            stock[name] = int(quantity)
    return stock


def save_ingredients(stock):
    with STOCK_FILE.open("w") as file:
        for name, quantity in stock.items():
            file.write(f"{name}:{quantity}\n")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/menu")
def menu():
    return jsonify({
        "pizza": list(pizza_ingredients.keys()),
        "burger": list(burger_ingredients.keys())
    })


@app.get("/api/stock")
def get_stock():
    return jsonify(read_ingredients())


@app.route("/api/orders", methods=["POST"])
def create_order():
    if request.is_json:
        data = request.get_json(silent=True)
    else:
        data = request.form

    if not data:
        return jsonify({"error": "Please enter order details"}), 400

    food = data.get("food", "").lower()
    food_type = data.get("type", "").lower()
    quantity = data.get("quantity", "")

    if food not in ("pizza", "burger"):
        return jsonify({"error": "Choose pizza or burger"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    recipes = pizza_ingredients if food == "pizza" else burger_ingredients

    if food_type not in recipes:
        return jsonify({
            "error": f"{food_type} is not available for {food}"
        }), 400

    stock = read_ingredients()
    recipe = recipes[food_type]

    required_stock = {
        name: amount * quantity
        for name, amount in recipe.items()
    }

    for name, amount in required_stock.items():
        if name not in stock:
            return jsonify({"error": f"{name} is missing from stock"}), 500

        if stock[name] < amount:
            return jsonify({
                "error": f"Not enough {name}. Available: {stock[name]}"
            }), 400

    for name, amount in required_stock.items():
        stock[name] -= amount

    save_ingredients(stock)

    if request.is_json:
        return jsonify({
            "message": "Order placed successfully",
            "food": food,
            "type": food_type,
            "quantity": quantity,
            "remaining_stock": stock
        }), 201

    return render_template(
        "success.html",
        food=food,
        food_type=food_type,
        quantity=quantity
    )
@app.get("/stock")
def stock_page():
    stock = read_ingredients()
    return render_template("stock.html", stock=stock)

if __name__ == "__main__":
    app.run(debug=True)
