"""Write fake_tools/indomain.json: 48 retail tools that a real store could offer but no task needs.

kind "indomain", subtype "in_domain_other_function", sibling null, no rank.
dorig = the text below in the style of the retail docstrings; dmin = first sentence, no params.
drich is added later by scripts/generate_drich.py --which indomain.
Rule: no dorig claims a job a real retail tool does (look up users, orders, items or products;
cancel, return, exchange or modify an order; change a user address; transfer to a human).

Usage: python scripts/build_indomain.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERROR = "This service is currently unavailable."

P = {  # shared parameter text, copied from the retail docstrings where the parameter exists there
    "user_id": ("str", "The user id, such as 'sara_doe_496'."),
    "item_id": ("str", "The item id, such as '6086499569'. Be careful the item id is different from the product id."),
    "product_id": ("str", "The product id, such as '6086499569'. Be careful the product id is different from the item id."),
    "order_id": ("str", "The order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id."),
    "zip": ("str", "The zip code, such as '12345'."),
    "email": ("str", "The email of the user, such as 'something@example.com'."),
    "recipient_email": ("str", "The email of the recipient, such as 'something@example.com'."),
    "store_id": ("str", "The store id, such as 'store_0000'."),
    "subscription_id": ("str", "The subscription id, such as 'sub_0000000'."),
}

# (category, name, description, [(param, type, text) or shared param name])
TOOLS = [
    ("Promotions", "apply_coupon_code", "Apply a coupon code to the user's shopping cart. The discount is shown at checkout.",
     ["user_id", ("coupon_code", "str", "The coupon code, such as 'SAVE10'.")]),
    ("Promotions", "list_active_promotions", "List the promotions that are currently active in a product category.",
     [("category", "str", "The product category, such as 'Electronics', or 'all'.")]),
    ("Promotions", "check_coupon_validity", "Check whether a coupon code is valid and when it expires.",
     [("coupon_code", "str", "The coupon code, such as 'SAVE10'.")]),
    ("Promotions", "get_flash_sale_schedule", "Get the schedule of flash sales for a given date.",
     [("date", "str", "The date in 'YYYY-MM-DD' format, such as '2024-05-01'.")]),
    ("Promotions", "get_bundle_offers", "Get the bundle discounts available when buying several units of a product together.",
     ["product_id", ("quantity", "int", "The number of units in the bundle, such as 2.")]),
    ("Promotions", "subscribe_to_price_drop_alert", "Subscribe the user to an email alert for when the price of a product drops.",
     ["user_id", "product_id"]),
    ("Wishlist", "add_to_wishlist", "Add an item to the user's wishlist.", ["user_id", "item_id"]),
    ("Wishlist", "remove_from_wishlist", "Remove an item from the user's wishlist.", ["user_id", "item_id"]),
    ("Wishlist", "get_wishlist", "Get the items saved in the user's wishlist, 20 items per page.",
     ["user_id", ("page", "int", "The page number, starting from 1.")]),
    ("Wishlist", "share_wishlist", "Share the user's wishlist with another person by email.", ["user_id", "recipient_email"]),
    ("Cart", "add_item_to_cart", "Add an item to the user's shopping cart for a new purchase.",
     ["user_id", "item_id", ("quantity", "int", "The number of units to add, such as 1.")]),
    ("Cart", "get_cart_contents", "Get the items currently in the user's shopping cart.",
     ["user_id", ("include_saved", "bool", "Whether to also include items saved for later.")]),
    ("Cart", "clear_cart", "Remove all items from the user's shopping cart.",
     ["user_id", ("confirm", "bool", "Must be true to clear the cart.")]),
    ("Cart", "save_cart_for_later", "Save the current shopping cart under a name so the user can restore it later.",
     ["user_id", ("cart_name", "str", "A name for the saved cart, such as 'birthday gifts'.")]),
    ("Stores and pickup", "find_nearby_stores", "Find physical stores near a zip code.",
     ["zip", ("radius_miles", "int", "The search radius in miles, such as 10.")]),
    ("Stores and pickup", "get_store_hours", "Get the opening hours of a physical store.", ["store_id"]),
    ("Stores and pickup", "check_in_store_availability", "Check whether an item is in stock at a physical store.",
     ["item_id", "store_id"]),
    ("Stores and pickup", "schedule_store_pickup", "Schedule an in-store pickup time for an order placed with store pickup.",
     ["order_id", "store_id", ("pickup_date", "str", "The pickup date in 'YYYY-MM-DD' format, such as '2024-05-01'.")]),
    ("Stores and pickup", "get_curbside_pickup_instructions", "Get the curbside pickup instructions for an order placed with store pickup.",
     ["order_id", "store_id"]),
    ("Gifts", "add_gift_wrapping", "Add gift wrapping to an order before it ships.",
     ["order_id", ("wrap_style", "str", "The wrapping style, such as 'classic' or 'birthday'.")]),
    ("Gifts", "add_gift_message", "Add a printed gift message to the packing slip of an order.",
     ["order_id", ("message", "str", "The gift message, up to 200 characters.")]),
    ("Gifts", "purchase_gift_card", "Buy a new electronic gift card and send it to a recipient by email.",
     ["user_id", ("amount", "float", "The gift card amount in dollars, such as 50.0."), "recipient_email"]),
    ("Gifts", "create_gift_registry", "Create a gift registry for an event such as a wedding or a birthday.",
     ["user_id", ("event_date", "str", "The event date in 'YYYY-MM-DD' format, such as '2024-05-01'.")]),
    ("Product content", "get_size_guide", "Get the size chart for a product.",
     ["product_id", ("region", "str", "The sizing region, such as 'US' or 'EU'.")]),
    ("Product content", "compare_products", "Compare the features of several products side by side.",
     [("product_ids", "list[str]", "The product ids to compare, each such as '6086499569'.")]),
    ("Product content", "get_product_recommendations", "Get personalized product recommendations for the user.",
     ["user_id", ("limit", "int", "The maximum number of recommendations, such as 5.")]),
    ("Product content", "get_care_instructions", "Get the washing and care instructions for a product.",
     ["product_id", ("language", "str", "The language code, such as 'en' or 'es'.")]),
    ("Product content", "ask_product_question", "Post a question about a product to the community questions and answers page.",
     ["product_id", ("question", "str", "The question, such as 'Is this waterproof?'.")]),
    ("Account settings", "update_communication_preferences", "Update whether the user receives marketing emails and text messages.",
     ["user_id", ("email_opt_in", "bool", "Whether the user wants marketing emails."),
      ("sms_opt_in", "bool", "Whether the user wants marketing text messages.")]),
    ("Account settings", "send_password_reset", "Send the user a link to reset their website password.",
     ["email", ("channel", "str", "Where to send the link, either 'email' or 'sms'.")]),
    ("Account settings", "update_user_phone_number", "Update the phone number on the user's account.",
     ["user_id", ("phone_number", "str", "The new phone number, such as '555-123-4567'.")]),
    ("Account settings", "set_preferred_language", "Set the language used for the user's emails and website.",
     ["user_id", ("language", "str", "The language code, such as 'en' or 'es'.")]),
    ("Account settings", "enable_two_factor_auth", "Turn on two-factor sign-in for the user's website account.",
     ["user_id", ("method", "str", "The second factor, either 'sms' or 'authenticator_app'.")]),
    ("Subscriptions", "create_auto_reorder", "Set up automatic repeat delivery of an item at a fixed interval.",
     ["user_id", "item_id", ("interval_days", "int", "The number of days between deliveries, such as 30.")]),
    ("Subscriptions", "pause_subscription", "Pause a repeat-delivery subscription until a given date.",
     ["subscription_id", ("until_date", "str", "The date to resume in 'YYYY-MM-DD' format, such as '2024-05-01'.")]),
    ("Subscriptions", "list_user_subscriptions", "List the user's repeat-delivery subscriptions.",
     ["user_id", ("status", "str", "Which subscriptions to list: 'active', 'paused' or 'all'.")]),
    ("Subscriptions", "skip_next_delivery", "Skip the next scheduled delivery of a repeat-delivery subscription.",
     ["subscription_id"]),
    ("Protection plans", "purchase_protection_plan", "Buy an extended protection plan for an item.",
     ["item_id", ("plan_years", "int", "The plan length in years, from 1 to 3.")]),
    ("Protection plans", "get_warranty_info", "Get the manufacturer warranty terms for an item.",
     ["item_id", ("purchase_date", "str", "The purchase date in 'YYYY-MM-DD' format, such as '2024-05-01'.")]),
    ("Protection plans", "register_product_warranty", "Register an item's serial number with the manufacturer warranty program.",
     ["item_id", ("serial_number", "str", "The serial number printed on the item, such as 'SN12345678'.")]),
    ("Financing", "apply_for_store_credit_card", "Start an application for the store credit card.",
     ["user_id", ("annual_income", "float", "The applicant's annual income in dollars, such as 55000.0.")]),
    ("Financing", "get_financing_options", "Get the monthly financing plans available for a product.",
     ["product_id", ("months", "int", "The plan length in months, such as 12.")]),
    ("Financing", "get_installment_plan_status", "Get the remaining balance and next due date of an installment plan.",
     ["user_id", ("plan_id", "str", "The installment plan id, such as 'plan_0000000'.")]),
    ("Shipping information", "get_shipping_rates", "Get the shipping rates for a package of a given weight to a zip code.",
     ["zip", ("weight_lbs", "float", "The package weight in pounds, such as 2.5.")]),
    ("Shipping information", "estimate_delivery_date", "Estimate the delivery date of a new purchase shipped to a zip code.",
     ["zip", ("shipping_speed", "str", "The shipping speed: 'standard', 'express' or 'overnight'.")]),
    ("Feedback", "submit_site_feedback", "Submit feedback about the shopping website.",
     ["user_id", ("rating", "int", "The rating from 1 to 5."), ("comment", "str", "The feedback text.")]),
    ("Feedback", "report_website_issue", "Report a technical problem with the website or the app.",
     ["user_id", ("description", "str", "A description of the problem.")]),
    ("Feedback", "notify_when_back_in_stock", "Email the user when an out-of-stock item is available again.",
     ["user_id", "item_id"]),
]


def first_sentence(text):
    return re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]


def main():
    out = []
    for category, name, desc, params in TOOLS:
        ps = [(p, *P[p]) if isinstance(p, str) else p for p in params]
        out.append({
            "name": name, "kind": "indomain", "subtype": "in_domain_other_function", "sibling": None,
            "category": category,
            "params": [{"name": n, "type": t, "required": True} for n, t, _ in ps],
            "error": ERROR,
            "desc": {"dorig": {"desc": desc, "params": {n: d for n, _, d in ps}},
                     "dmin": {"desc": first_sentence(desc), "params": {}}},
        })
    path = ROOT / "fake_tools" / "indomain.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"wrote {len(out)} in-domain tools -> {path}")


if __name__ == "__main__":
    main()
