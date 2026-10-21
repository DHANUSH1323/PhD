"""Build fake_tools/lookalike.json: 64 look-alike tools, 4 per real retail tool.

Names, ranks and error messages follow STEP4_SPEC.md Section 7 (Oct 14, part B).
Parameters are read from the sibling's real signature, so every look-alike copies
its sibling's parameters exactly (names, types, required). Parameter descriptions
are the sibling's dorig text unless the scope needs a different wording, in which
case the override is listed in LOOKALIKES below.

dorig = the description below + parameter text.  dmin = first sentence, no params.
drich is added later by scripts/generate_drich.py --which lookalike.

Usage: PYTHONPATH=. python scripts/build_lookalike.py
"""
import inspect
import json
import re
import typing
from pathlib import Path

from tau2.domains.retail.data_model import RetailDB
from tau2.domains.retail.tools import RetailTools
from tau2.domains.retail.utils import RETAIL_DB_PATH

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fake_tools" / "lookalike.json"

# Error messages by name pattern (spec Section 7, part B). Checked in this order.
ERR_VERSION = "This version of the service is not available for this account."
ERR_ARCHIVED = "No archived record matches this request."
ERR_BUSINESS = "No business account is linked to this customer."
ERR_MARKETPLACE = "This record is not a marketplace record."
ERR_GUEST = "No guest account matches this request."
ERR_GENERIC = "The request could not be completed."


def error_for(name: str, rank: int) -> str:
    if name in ("calculate_order_total", "calculate_tax"):
        return ERR_GENERIC
    if rank == 3:
        return ERR_GENERIC
    if "_legacy" in name or "_v1" in name:
        return ERR_VERSION
    if "_archived" in name:
        return ERR_ARCHIVED
    if "business" in name:
        return ERR_BUSINESS
    if "marketplace" in name:
        return ERR_MARKETPLACE
    if "guest" in name:
        return ERR_GUEST
    # transfer_to_billing_department (rank 2) matches no pattern in the spec table.
    return ERR_GENERIC


# Shared scope sentences, so the same scope is worded the same way everywhere.
LEGACY_ORDER = "Orders placed on the current platform are not handled by this function."
LEGACY_DIR = "Only accounts that were migrated from the previous platform are listed in this directory."
V1 = "Version 1 is retained for accounts created before the service upgrade."
BUSINESS = "Orders placed under a personal account are not handled by this function."
MARKETPLACE = "Orders fulfilled directly by the store are not handled by this function."
GUEST = "Guest users checked out without creating an account."

# name: (sibling, rank, subtype, description, {param: override description})
LOOKALIKES = {
    # ---- rank 1: near_duplicate, legacy / archived ---------------------------------
    "calculate_legacy": ("calculate", 1, "near_duplicate",
        "Calculate the result of a mathematical expression using the legacy calculation service. "
        "The legacy service is retained for accounts that were migrated from the previous platform.", {}),
    "cancel_order_legacy": ("cancel_pending_order", 1, "near_duplicate",
        f"Cancel a pending order that was placed on the legacy ordering platform. {LEGACY_ORDER}", {}),
    "exchange_items_legacy": ("exchange_delivered_order_items", 1, "near_duplicate",
        "Exchange items in a delivered order that was placed on the legacy ordering platform to new items "
        f"of the same product type. {LEGACY_ORDER}", {}),
    "find_user_id_by_email_legacy": ("find_user_id_by_email", 1, "near_duplicate",
        f"Find user id by email in the legacy customer directory. {LEGACY_DIR}", {}),
    "find_user_id_by_name_zip_legacy": ("find_user_id_by_name_zip", 1, "near_duplicate",
        f"Find user id by first name, last name, and zip code in the legacy customer directory. {LEGACY_DIR}", {}),
    "get_item_details_archived": ("get_item_details", 1, "near_duplicate",
        "Get the inventory details of an archived item. "
        "Items are archived once they have been out of stock for more than two years.",
        {"item_id": "The archived item id, such as '6086499569'. Be careful the item id is different from the product id."}),
    "get_order_details_archived": ("get_order_details", 1, "near_duplicate",
        "Get the status and details of an archived order. "
        "Orders are archived two years after they are delivered or cancelled.",
        {"order_id": "The archived order id, such as '#W0000000'. Be careful there is a '#' symbol at the beginning of the order id."}),
    "get_product_details_archived": ("get_product_details", 1, "near_duplicate",
        "Get the inventory details of an archived product. "
        "Products are archived once they have been discontinued for more than two years.",
        {"product_id": "The archived product id, such as '6086499569'. Be careful the product id is different from the item id."}),
    "get_user_details_legacy": ("get_user_details", 1, "near_duplicate",
        "Get the details of a user from the legacy customer directory, including the orders they placed "
        f"on the previous platform. {LEGACY_DIR}", {}),
    "list_all_product_types_legacy": ("list_all_product_types", 1, "near_duplicate",
        "List the name and product id of all product types in the legacy catalog. "
        "The legacy catalog contains the product types that were sold on the previous platform.", {}),
    "modify_order_address_legacy": ("modify_pending_order_address", 1, "near_duplicate",
        f"Modify the shipping address of a pending order that was placed on the legacy ordering platform. {LEGACY_ORDER}", {}),
    "modify_order_items_legacy": ("modify_pending_order_items", 1, "near_duplicate",
        "Modify items in a pending order that was placed on the legacy ordering platform to new items "
        f"of the same product type. {LEGACY_ORDER}", {}),
    "modify_order_payment_legacy": ("modify_pending_order_payment", 1, "near_duplicate",
        f"Modify the payment method of a pending order that was placed on the legacy ordering platform. {LEGACY_ORDER}", {}),
    "modify_user_address_legacy": ("modify_user_address", 1, "near_duplicate",
        f"Modify the default address of a user in the legacy customer directory. {LEGACY_DIR}", {}),
    "return_items_legacy": ("return_delivered_order_items", 1, "near_duplicate",
        f"Return some items of a delivered order that was placed on the legacy ordering platform. {LEGACY_ORDER}", {}),
    "transfer_to_human_agents_legacy": ("transfer_to_human_agents", 1, "near_duplicate",
        "Transfer the user to a human agent through the legacy support queue, with a summary of the user's issue. "
        "The legacy queue serves accounts that were migrated from the previous platform.", {}),

    # ---- rank 2: near_duplicate, business / marketplace ---------------------------
    "calculate_order_total": ("calculate", 2, "near_duplicate",
        "Calculate the total of an order from a mathematical expression of its line items. "
        "The expression should combine item prices, quantities, and any discounts.",
        {"expression": "The expression combining line item prices and quantities, such as '2 * 19.99 + 5.00'. "
                       "The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces."}),
    "cancel_business_order": ("cancel_pending_order", 2, "near_duplicate",
        f"Cancel a pending order placed under a business account. {BUSINESS}", {}),
    "exchange_marketplace_order_items": ("exchange_delivered_order_items", 2, "near_duplicate",
        "Exchange items in a delivered marketplace order, fulfilled by a third-party seller, to new items "
        f"of the same product type. {MARKETPLACE}", {}),
    "find_business_user_by_email": ("find_user_id_by_email", 2, "near_duplicate",
        "Find the user id of a business account by the email of its registered contact. "
        "Personal accounts are not listed in the business directory.",
        {"email": "The email of the registered contact of the business account, such as 'something@example.com'."}),
    "find_business_user_by_name_zip": ("find_user_id_by_name_zip", 2, "near_duplicate",
        "Find the user id of a business account by the first name, last name, and zip code of its registered contact. "
        "Personal accounts are not listed in the business directory.",
        {"first_name": "The first name of the registered contact, such as 'John'.",
         "last_name": "The last name of the registered contact, such as 'Doe'.",
         "zip": "The zip code of the business account, such as '12345'."}),
    "get_marketplace_item_details": ("get_item_details", 2, "near_duplicate",
        "Get the inventory details of a marketplace item, sold by a third-party seller. "
        "Items stocked directly by the store are not handled by this function.", {}),
    "get_marketplace_order_details": ("get_order_details", 2, "near_duplicate",
        f"Get the status and details of a marketplace order, fulfilled by a third-party seller. {MARKETPLACE}", {}),
    "get_marketplace_product_details": ("get_product_details", 2, "near_duplicate",
        "Get the inventory details of a marketplace product, sold by a third-party seller. "
        "Products stocked directly by the store are not handled by this function.", {}),
    "get_business_user_details": ("get_user_details", 2, "near_duplicate",
        "Get the details of a business account, including the orders placed under it. "
        "Personal accounts are not handled by this function.",
        {"user_id": "The user id of the business account, such as 'sara_doe_496'."}),
    "list_marketplace_product_types": ("list_all_product_types", 2, "near_duplicate",
        "List the name and product id of all product types offered by third-party marketplace sellers. "
        "Product types stocked directly by the store are not included.", {}),
    "modify_business_order_address": ("modify_pending_order_address", 2, "near_duplicate",
        f"Modify the shipping address of a pending order placed under a business account. {BUSINESS}", {}),
    "modify_marketplace_order_items": ("modify_pending_order_items", 2, "near_duplicate",
        "Modify items in a pending marketplace order, fulfilled by a third-party seller, to new items "
        f"of the same product type. {MARKETPLACE}", {}),
    "modify_business_order_payment": ("modify_pending_order_payment", 2, "near_duplicate",
        f"Modify the payment method of a pending order placed under a business account. {BUSINESS}", {}),
    "modify_business_user_address": ("modify_user_address", 2, "near_duplicate",
        "Modify the default address of a business account. Personal accounts are not handled by this function.",
        {"user_id": "The user id of the business account, such as 'sara_doe_496'."}),
    "return_marketplace_order_items": ("return_delivered_order_items", 2, "near_duplicate",
        f"Return some items of a delivered marketplace order, fulfilled by a third-party seller. {MARKETPLACE}", {}),
    "transfer_to_billing_department": ("transfer_to_human_agents", 2, "near_duplicate",
        "Transfer the user to the billing department, with a summary of the user's issue. "
        "The billing department handles invoice and payment disputes for business accounts.", {}),

    # ---- rank 3: schema_compatible, same arguments, different effect --------------
    "calculate_tax": ("calculate", 3, "schema_compatible",
        "Calculate the sales tax due on an amount given as a mathematical expression. "
        "The result is the tax amount only, not the total.",
        {"expression": "The expression giving the taxable amount, such as '19.99 * 2'. "
                       "The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces."}),
    "hold_pending_order": ("cancel_pending_order", 3, "schema_compatible",
        "Place a pending order on hold so that it is not processed until the hold is released. "
        "The order stays pending and is not cancelled.",
        {"reason": "The reason for the hold, which should be either 'awaiting payment' or 'customer request'."}),
    "request_exchange_quote": ("exchange_delivered_order_items", 3, "schema_compatible",
        "Request a price quote for exchanging items in a delivered order to new items of the same product type. "
        "No exchange is performed; the quote shows the price difference that would apply.", {}),
    "find_marketing_contact_by_email": ("find_user_id_by_email", 3, "schema_compatible",
        "Find the marketing contact id associated with an email. "
        "Marketing contacts are newsletter subscribers and are not the same as user accounts.",
        {"email": "The email of the marketing contact, such as 'something@example.com'."}),
    "lookup_loyalty_member_by_name_zip": ("find_user_id_by_name_zip", 3, "schema_compatible",
        "Look up a loyalty program member id by first name, last name, and zip code. "
        "Loyalty member ids are not the same as user ids.",
        {"first_name": "The first name of the member, such as 'John'.",
         "last_name": "The last name of the member, such as 'Doe'.",
         "zip": "The zip code of the member, such as '12345'."}),
    "get_item_price_history": ("get_item_details", 3, "schema_compatible",
        "Get the price history of an item over the past twelve months. "
        "This function does not return current inventory details.", {}),
    "get_order_shipment_tracking": ("get_order_details", 3, "schema_compatible",
        "Get the carrier tracking events for the shipments of an order. "
        "This function does not return the order's items, payment, or status.", {}),
    "get_product_reviews": ("get_product_details", 3, "schema_compatible",
        "Get the customer reviews of a product. This function does not return inventory details.", {}),
    "get_user_loyalty_points": ("get_user_details", 3, "schema_compatible",
        "Get the loyalty points balance of a user. This function does not return the user's profile or orders.", {}),
    "list_discontinued_product_types": ("list_all_product_types", 3, "schema_compatible",
        "List the name and product id of all product types that have been discontinued. "
        "Discontinued product types can no longer be ordered.", {}),
    "validate_order_address": ("modify_pending_order_address", 3, "schema_compatible",
        "Validate a shipping address against the postal database for a pending order. "
        "The order's shipping address is not changed.", {}),
    "preview_order_item_change": ("modify_pending_order_items", 3, "schema_compatible",
        "Preview the price difference of changing items in a pending order to new items of the same product type. "
        "The order is not modified.", {}),
    "authorize_order_payment": ("modify_pending_order_payment", 3, "schema_compatible",
        "Authorize a payment method for a pending order without changing the order's payment method. "
        "The authorization holds funds until the order is processed.",
        {"payment_method_id": "The payment method id to authorize, such as 'gift_card_0000000' or 'credit_card_0000000'. "
                              "These can be looked up from the user or order details."}),
    "verify_user_address": ("modify_user_address", 3, "schema_compatible",
        "Verify that an address matches the postal database and is deliverable. "
        "The user's default address is not changed.", {}),
    "request_return_label": ("return_delivered_order_items", 3, "schema_compatible",
        "Request a prepaid return shipping label for items of a delivered order. "
        "No return is recorded; the label is emailed to the user.",
        {"payment_method_id": "The payment method id on the order, such as 'gift_card_0000000' or 'credit_card_0000000'. "
                              "These can be looked up from the user or order details."}),
    "create_support_ticket": ("transfer_to_human_agents", 3, "schema_compatible",
        "Create a support ticket with a summary of the user's issue for later follow-up by email. "
        "The user is not transferred and the conversation continues.", {}),

    # ---- rank 4: near_duplicate reserve, v1 / guest --------------------------------
    "calculate_v1": ("calculate", 4, "near_duplicate",
        f"Calculate the result of a mathematical expression using version 1 of the calculation service. {V1}", {}),
    "cancel_pending_order_v1": ("cancel_pending_order", 4, "near_duplicate",
        f"Cancel a pending order using version 1 of the order service. {V1}", {}),
    "exchange_delivered_order_items_v1": ("exchange_delivered_order_items", 4, "near_duplicate",
        "Exchange items in a delivered order to new items of the same product type using version 1 "
        f"of the order service. {V1}", {}),
    "find_guest_user_by_email": ("find_user_id_by_email", 4, "near_duplicate",
        f"Find the guest user id associated with an email. {GUEST}",
        {"email": "The email of the guest user, such as 'something@example.com'."}),
    "find_guest_user_by_name_zip": ("find_user_id_by_name_zip", 4, "near_duplicate",
        f"Find the guest user id by first name, last name, and zip code. {GUEST}",
        {"first_name": "The first name of the guest user, such as 'John'.",
         "last_name": "The last name of the guest user, such as 'Doe'.",
         "zip": "The zip code of the guest user, such as '12345'."}),
    "get_item_details_v1": ("get_item_details", 4, "near_duplicate",
        f"Get the inventory details of an item using version 1 of the catalog service. {V1}", {}),
    "get_order_summary_v1": ("get_order_details", 4, "near_duplicate",
        "Get a summary of an order using version 1 of the order service. "
        f"The summary contains the order status and item count. {V1}", {}),
    "get_product_details_v1": ("get_product_details", 4, "near_duplicate",
        f"Get the inventory details of a product using version 1 of the catalog service. {V1}", {}),
    "get_user_profile_v1": ("get_user_details", 4, "near_duplicate",
        f"Get the profile of a user using version 1 of the customer service, including their orders. {V1}", {}),
    "list_product_categories_v1": ("list_all_product_types", 4, "near_duplicate",
        f"List the name and product id of all product categories using version 1 of the catalog service. {V1}", {}),
    "modify_pending_order_address_v1": ("modify_pending_order_address", 4, "near_duplicate",
        f"Modify the shipping address of a pending order using version 1 of the order service. {V1}", {}),
    "modify_pending_order_items_v1": ("modify_pending_order_items", 4, "near_duplicate",
        "Modify items in a pending order to new items of the same product type using version 1 "
        f"of the order service. {V1}", {}),
    "modify_pending_order_payment_v1": ("modify_pending_order_payment", 4, "near_duplicate",
        f"Modify the payment method of a pending order using version 1 of the order service. {V1}", {}),
    "modify_user_address_v1": ("modify_user_address", 4, "near_duplicate",
        f"Modify the default address of a user using version 1 of the customer service. {V1}", {}),
    "return_delivered_order_items_v1": ("return_delivered_order_items", 4, "near_duplicate",
        f"Return some items of a delivered order using version 1 of the order service. {V1}", {}),
    "transfer_to_human_agents_v1": ("transfer_to_human_agents", 4, "near_duplicate",
        "Transfer the user to a human agent using version 1 of the support service, with a summary "
        f"of the user's issue. {V1}", {}),
}


def type_name(annotation) -> str:
    """Map a real tool's annotation to the harness TYPE_MAP key."""
    if annotation is str:
        return "str"
    if annotation is int:
        return "int"
    if annotation is float:
        return "float"
    if annotation is bool:
        return "bool"
    if annotation is dict:
        return "dict"
    origin = typing.get_origin(annotation)
    if origin in (list, typing.List):
        return "list[str]"
    raise ValueError(f"Unsupported annotation {annotation!r}")


def first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s", " ".join(text.split()), maxsplit=1)[0]


def main():
    kit = RetailTools(RetailDB.load(RETAIL_DB_PATH))
    dorig = json.loads((ROOT / "descriptions" / "dorig.json").read_text())
    real_names = set(kit._func_tools)
    specs = []
    for name, (sibling, rank, subtype, desc, overrides) in LOOKALIKES.items():
        assert sibling in real_names, f"{name}: unknown sibling {sibling}"
        assert set(overrides) <= set(dorig[sibling]["params"]), f"{name}: override for unknown param"
        sig = inspect.signature(getattr(kit, sibling))
        params = [{"name": p.name, "type": type_name(p.annotation),
                   "required": p.default is inspect.Parameter.empty}
                  for p in sig.parameters.values()]
        pdesc = {k: overrides.get(k, v) for k, v in dorig[sibling]["params"].items()}
        specs.append({
            "name": name, "kind": "lookalike", "sibling": sibling, "rank": rank, "subtype": subtype,
            "params": params, "error": error_for(name, rank),
            "desc": {"dmin": {"desc": first_sentence(desc), "params": {}},
                     "dorig": {"desc": desc, "params": pdesc}},
        })

    # Acceptance checks (spec Section 7, part B)
    names = [s["name"] for s in specs]
    assert len(specs) == 64, len(specs)
    assert len(set(names)) == 64, "duplicate names"
    assert not set(names) & real_names, set(names) & real_names
    for r in (1, 2, 3, 4):
        assert sum(s["rank"] == r for s in specs) == 16, f"rank {r}"
    for sib in sorted(real_names):
        assert sum(s["sibling"] == sib for s in specs) == 4, sib
    assert all(s["desc"]["dmin"]["desc"] and s["desc"]["dorig"]["desc"] for s in specs)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(specs, indent=2) + "\n")
    print(f"wrote {len(specs)} look-alikes -> {OUT}")


if __name__ == "__main__":
    main()
