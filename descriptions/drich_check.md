# Hand-check of drich against tools.py and policy.md

One row per sentence. Fill the last column with the enforcing line in tools.py (for example `tools.py:214`) or `NOT ENFORCED`. Delete from the json any sentence marked NOT ENFORCED that states a constraint, and any sentence flagged POLICY that is absent from dorig.


## calculate

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Evaluates a mathematical expression and returns the computed result. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 2 | Use this API when you need to perform arithmetic calculations, including addition, subtraction, multiplication, and division, with support for parentheses to control order of operations. |  |  |  | |
| 3 | Do NOT use this API for symbolic algebra, equation solving, non-arithmetic operations (e.g., trigonometric functions, logarithms), or any task that does not involve computing a numerical result from a mathematical expression. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 4 | Parameters: - expression (string, required): A mathematical expression to evaluate. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 5 | The expression must be composed of numbers, arithmetic operators (+, -, *, /), parentheses for grouping, and optional spaces for readability. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 6 | No other characters, functions, or variable names are supported. |  |  | 155: `raise ValueError("Invalid characters in expression")` | |
| 7 | The expression must be a complete, syntactically valid mathematical expression that can be evaluated to a single numerical result. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 8 | Common validation failures and how to avoid them: - Do not include unsupported characters or function names (e.g., sqrt, sin, log, ^, %). |  |  | 155: `raise ValueError("Invalid characters in expression")` | |
| 9 | Stick strictly to numbers, +, -, *, /, and parentheses. |  |  |  | |
| 10 | - Ensure parentheses are balanced; every opening parenthesis must have a corresponding closing parenthesis. |  |  |  | |
| 11 | - Avoid division by zero within the expression, as this will likely cause an error. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 12 | - Do not pass an empty string; the expression must contain at least one valid numerical computation. |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |
| 13 | - Ensure the expression is syntactically valid (e.g., avoid consecutive operators like '2 ++ 3' or trailing operators like '2 +'). |  |  | 154: `if not all(char in "0123456789+-*/(). " for char in expressi`<br>155: `raise ValueError("Invalid characters in expression")`<br>156: `return str(round(float(eval(expression, {"__builtins__": Non` | |

## cancel_pending_order

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | cancel_pending_order: Cancels an order that is currently in 'pending' status. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 2 | Use this API when a user explicitly requests to cancel an order that has not yet been processed or delivered. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 164: `The refund will be added to the user's gift card balance imm`<br>166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":` | |
| 3 | Do NOT use this API if the order has already been processed, shipped, or delivered, as cancellation is only possible for pending orders. |  | POLICY: Orders can have other optional attributes based on the actions that have been ta | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 4 | Before calling this API, the agent must clearly explain the cancellation details to the user and obtain explicit confirmation (yes/no) to proceed. |  | POLICY: Before taking any action that updates the database (cancel, modify, return, exch | 164: `The refund will be added to the user's gift card balance imm`<br>166: `The function returns the order details after the cancellatio` | |
| 5 | Without user confirmation, do not invoke this API. |  | POLICY: Before taking any action that updates the database (cancel, modify, return, exch | 164: `The refund will be added to the user's gift card balance imm` | |
| 6 | Upon successful cancellation, the order status changes to 'cancelled' and a refund is issued. |  |  | 164: `The refund will be added to the user's gift card balance imm`<br>166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":` | |
| 7 | If the original payment was made via gift card, the refund is applied to the user's gift card balance immediately. |  | POLICY: After user confirmation, the order status will be changed to 'cancelled', and th | 164: `The refund will be added to the user's gift card balance imm`<br>196: `if isinstance(payment_method, GiftCard):  # refund to gift c` | |
| 8 | For all other payment methods, the refund takes 5-7 business days to process. |  |  | 164: `The refund will be added to the user's gift card balance imm`<br>196: `if isinstance(payment_method, GiftCard):  # refund to gift c` | |
| 9 | The API returns the updated order details after cancellation. |  |  | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 10 | Parameters: 1. |  |  |  | |
| 11 | order_id (string, required): The unique identifier of the order to cancel. |  |  | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 12 | This value must begin with the '#' character followed by the order number (e.g., formatted as '#W' followed by digits). |  |  | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 13 | A common mistake is omitting the leading '#' symbol; ensure it is always included. |  |  | 181: `if reason not in {"no longer needed", "ordered by mistake"}:` | |
| 14 | 2. |  |  |  | |
| 15 | reason (string, required): The reason for the cancellation. |  | POLICY: Orders can have other optional attributes based on the actions that have been ta | 166: `The function returns the order details after the cancellatio`<br>181: `if reason not in {"no longer needed", "ordered by mistake"}:`<br>182: `raise ValueError("Invalid reason")` | |
| 16 | This parameter is strictly constrained to one of two allowed values: 'no longer needed' or 'ordered by mistake'. |  |  | 181: `if reason not in {"no longer needed", "ordered by mistake"}:` | |
| 17 | Any other value will be rejected. |  |  |  | |
| 18 | The agent should determine the appropriate reason based on the user's stated intent. |  |  | 164: `The refund will be added to the user's gift card balance imm`<br>181: `if reason not in {"no longer needed", "ordered by mistake"}:`<br>182: `raise ValueError("Invalid reason")` | |
| 19 | Validation and common failure points: - Supplying an order_id without the '#' prefix will fail validation. |  |  |  | |
| 20 | - Providing a reason value other than the two permitted strings will be rejected. |  |  | 181: `if reason not in {"no longer needed", "ordered by mistake"}:`<br>182: `raise ValueError("Invalid reason")` | |
| 21 | - Attempting to cancel an order that is not in 'pending' status (e.g., already processed or delivered) will fail. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 166: `The function returns the order details after the cancellatio`<br>177: `if order.status != "pending":`<br>178: `raise ValueError("Non-pending order cannot be cancelled")` | |
| 22 | - Both parameters are required; omitting either will result in an error. |  |  |  | |
| 23 | - There are no optional parameters, default values, or cross-parameter dependencies. |  |  |  | |

## exchange_delivered_order_items

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | exchange_delivered_order_items: Exchanges one or more items in a delivered order for new items of the same product type. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 2 | Use this API when a customer wants to swap specific items in an order that has already been delivered for different variants (e.g., different size, color, or configuration) of the same product. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 3 | Do NOT use this API for orders that have not yet been delivered, for returning items without replacement, for canceling orders, or for exchanging items for entirely different products. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 4 | For any given delivered order, a return or exchange operation can only be performed once; once an exchange has been processed, no further exchanges or returns can be made on that order. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 5 | Before calling this API, the agent must clearly explain the exchange details to the user and obtain explicit confirmation (yes/no) to proceed. |  | POLICY: Before taking any action that updates the database (cancel, modify, return, exch | 216: `For a delivered order, return or exchange can be only done o` | |
| 6 | Parameters (all required): 1. |  |  |  | |
| 7 | order_id (string, required): The unique identifier of the delivered order. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 8 | Must include the leading '#' character (e.g., formatted as '#W' followed by digits). |  |  |  | |
| 9 | Omitting the '#' prefix will likely cause a validation failure. |  |  |  | |
| 10 | 2. |  |  |  | |
| 11 | item_ids (array of strings, required): The list of item IDs to be exchanged out of the order. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 12 | Each item ID is a numeric string. |  |  | 255: `item = next((item for item in order.items if item.item_id ==`<br>256: `if item is None:`<br>257: `raise ValueError(f"Item {item_id} not found")` | |
| 13 | If the customer wants to exchange multiple units of the same item, the same item ID should appear multiple times in the list. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>255: `item = next((item for item in order.items if item.item_id ==`<br>256: `if item is None:` | |
| 14 | Every item ID listed must belong to the specified order. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 15 | 3. |  |  |  | |
| 16 | new_item_ids (array of strings, required): The list of replacement item IDs that the customer wants to receive. |  |  | 250: `if len(item_ids) != len(new_item_ids):`<br>255: `item = next((item for item in order.items if item.item_id ==`<br>256: `if item is None:` | |
| 17 | This array must be the same length as item_ids, and each entry corresponds positionally to the item in item_ids at the same index. |  |  | 246: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>250: `if len(item_ids) != len(new_item_ids):`<br>255: `item = next((item for item in order.items if item.item_id ==` | |
| 18 | Each new item must be of the same product type as the original item it replaces. |  | POLICY: For a pending order, each item can be modified to an available new item of the s | 255: `item = next((item for item in order.items if item.item_id ==`<br>256: `if item is None:`<br>257: `raise ValueError(f"Item {item_id} not found")` | |
| 19 | Mismatched product types between a pair of original and new item IDs will result in a validation failure. |  |  | 255: `item = next((item for item in order.items if item.item_id ==`<br>256: `if item is None:`<br>257: `raise ValueError(f"Item {item_id} not found")` | |
| 20 | Duplicate entries are allowed when exchanging multiple units. |  |  |  | |
| 21 | 4. |  |  |  | |
| 22 | payment_method_id (string, required): The payment method to be used for settling any price difference between the original and new items. |  |  | 251: `raise ValueError("The number of items to be exchanged should`<br>255: `item = next((item for item in order.items if item.item_id ==`<br>269: `# check payment method exists and can cover the price differ` | |
| 23 | If the new items cost more, this method will be charged; if they cost less, a refund will be issued to this method. |  |  | 251: `raise ValueError("The number of items to be exchanged should`<br>255: `item = next((item for item in order.items if item.item_id ==`<br>269: `# check payment method exists and can cover the price differ` | |
| 24 | The value should reference a valid payment method associated with the user or order, formatted as an identifier such as 'gift_card_' or 'credit_card_' followed by digits. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 25 | Using an invalid or unassociated payment method will cause a failure. |  |  | 269: `# check payment method exists and can cover the price differ` | |
| 26 | Key constraints and common mistakes to avoid: - The item_ids and new_item_ids arrays must have exactly the same number of elements; a mismatch will fail validation. |  |  | 246: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>247: `raise ValueError(f"Number of {item_id} not found.")`<br>250: `if len(item_ids) != len(new_item_ids):` | |
| 27 | - Each positional pair (item_ids[i], new_item_ids[i]) must refer to the same product category; you cannot swap an item for a different product. |  |  | 241: `raise ValueError("Non-delivered order cannot be exchanged")`<br>246: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>250: `if len(item_ids) != len(new_item_ids):` | |
| 28 | - Do not attempt to call this API more than once on the same order, as only one return or exchange is permitted per delivered order. |  |  | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 29 | - Ensure the order is in a delivered state before calling this API. |  | POLICY: ## Return delivered order An order can only be returned if its status is 'delive | 216: `For a delivered order, return or exchange can be only done o`<br>240: `if order.status != "delivered":`<br>241: `raise ValueError("Non-delivered order cannot be exchanged")` | |
| 30 | - Always confirm the full exchange details with the user and receive explicit approval before executing the call. |  |  | 216: `For a delivered order, return or exchange can be only done o` | |

## find_user_id_by_email

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Looks up a user's unique identifier using their email address. |  | POLICY: ### User Each user has a profile containing: - unique user id - email - default  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 2 | Use this API when you need to resolve an email address to a user ID, for instance before performing user-specific operations that require a user ID rather than an email. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 3 | Do not use this API if you already have the user ID or if you need to search for users by criteria other than email. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 4 | This API performs an exact lookup; if no user is associated with the provided email, an error message is returned. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 5 | Parameters: - email (string, required): The email address of the user to look up. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 6 | Must be a valid email address in standard format (e.g., local-part@domain). |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>328: `if user.email.lower() == email.lower():` | |
| 7 | Providing a malformed email or an email that does not correspond to any existing user will result in an error. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>322: `str: The user id if found, otherwise an error message.`<br>328: `if user.email.lower() == email.lower():` | |
| 8 | Ensure the email string is not empty, contains no leading or trailing whitespace, and follows conventional email formatting rules. |  |  | 316: `"""Find user id by email. If the user is not found, the func`<br>328: `if user.email.lower() == email.lower():` | |

## find_user_id_by_name_zip

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Looks up a customer's user ID using their first name, last name, and zip code. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |
| 2 | This is a fallback identification method and should only be used when the user cannot be found by email or when the user cannot remember their email address. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |
| 3 | Do not use this API as the first attempt to identify a user; attempt email-based lookup first. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |
| 4 | If no matching user is found for the provided combination of name and zip code, the API will return an error message. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |
| 5 | All three parameters are required: 'first_name' (string) is the customer's first name, 'last_name' (string) is the customer's last name, and 'zip' (string) is the customer's zip code. |  |  |  | |
| 6 | Note that zip is a string type, not a number, so it should preserve leading zeros and be passed as text. |  |  |  | |
| 7 | All three fields must match an existing customer record for a successful lookup; a mismatch in any single field will result in a not-found error. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |
| 8 | Common mistakes include omitting one of the required fields, passing zip as an integer instead of a string, or using this API before first attempting to locate the user by email. |  |  | 291: `will return an error message. By default, find user id by em`<br>292: `if the user is not found by email or cannot remember email.`<br>300: `str: The user id if found, otherwise an error message.` | |

## get_item_details

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Retrieves the inventory details of a specific item. |  |  | 378: `return item` | |
| 2 | Use this API when you need to look up detailed information about an individual item, such as its availability, stock levels, or other inventory-related attributes. |  |  | 378: `return item` | |
| 3 | Do NOT use this API to look up product-level information or when you only have a product ID rather than an item ID, as these are distinct identifiers. |  |  | 378: `return item` | |
| 4 | This API is not intended for searching, listing, or browsing items; it is strictly for retrieving details of a single, already-known item. |  |  | 378: `return item` | |
| 5 | Parameters: - item_id (string, required): The unique identifier for the item whose inventory details you want to retrieve. |  |  | 378: `return item` | |
| 6 | This must be a string value (e.g., a numeric string). |  |  |  | |
| 7 | It is critical to distinguish item IDs from product IDs — they are different concepts and are not interchangeable. |  |  | 378: `return item` | |
| 8 | Passing a product ID in place of an item ID will likely result in a failed lookup or incorrect results. |  |  | 378: `return item` | |
| 9 | Ensure you have obtained the correct item-level identifier before calling this API. |  |  | 378: `return item` | |
| 10 | Common validation failures and how to avoid them: - Providing a product ID instead of an item ID: These are separate identifiers. |  |  | 378: `return item` | |
| 11 | Verify that the ID you are using corresponds to an item, not a product. |  | POLICY: For example, for a 't-shirt' product, there could be a variant item with option  | 378: `return item` | |
| 12 | - Omitting item_id: This parameter is required and the call will fail without it. |  |  |  | |
| 13 | - Passing a non-string value: The item_id must be provided as a string, even if it appears numeric. |  |  |  | |

## get_order_details

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Retrieves the status and details of an existing order. |  |  | 346: `return order` | |
| 2 | Use this API when you need to look up information about a specific order, such as its current status, items, shipping details, or other order-related attributes. |  |  | 346: `return order` | |
| 3 | Do not use this API to create, modify, or cancel orders, nor to search for orders without a known order ID. |  |  | 346: `return order` | |
| 4 | Parameters: - order_id (string, required): The unique identifier for the order. |  |  | 346: `return order` | |
| 5 | This value must be a string that begins with the '#' character followed by a 'W' and seven digits (e.g., in the format '#W' followed by numeric characters). |  |  |  | |
| 6 | A common mistake is omitting the leading '#' symbol, which will result in a validation or lookup failure. |  |  |  | |
| 7 | Ensure the '#' prefix is always included when constructing this parameter. |  |  |  | |

## get_product_details

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Retrieves the inventory details of a specific product. |  |  | 362: `return product` | |
| 2 | Use this API when you need to look up inventory information (such as stock availability or product specifics) for a known product. |  |  | 362: `return product` | |
| 3 | Do not use this API to search for products by name, category, or other attributes; it requires an already-known product identifier. |  |  | 362: `return product` | |
| 4 | Do not use this API to look up information by item ID, as the product ID and item ID are distinct identifiers that are not interchangeable. |  |  | 362: `return product` | |
| 5 | Parameters: - product_id (string, required): The unique identifier for the product whose inventory details you want to retrieve. |  |  | 362: `return product` | |
| 6 | This is a string value, typically composed of digits (e.g., a numeric string). |  |  |  | |
| 7 | It is critical to distinguish this from an item ID — these are separate identifiers, and supplying an item ID in place of a product ID will not return correct results or may cause a validation failure. |  |  | 362: `return product` | |
| 8 | Ensure the value passed is specifically a product ID obtained from a context where product IDs are provided. |  |  | 362: `return product` | |
| 9 | Common mistakes to avoid: 1. |  |  |  | |
| 10 | Confusing product ID with item ID. |  | POLICY: For example, for a 't-shirt' product, there could be a variant item with option  | 362: `return product` | |
| 11 | These are different identifiers; using one in place of the other will lead to incorrect or failed lookups. |  |  |  | |
| 12 | 2. |  |  |  | |
| 13 | Passing a non-string value. |  |  |  | |
| 14 | The product_id must be provided as a string, even if it appears numeric. |  |  |  | |
| 15 | 3. |  |  |  | |
| 16 | Omitting the product_id parameter. |  |  |  | |
| 17 | It is required and the request will fail without it. |  |  |  | |
| 18 | 4. |  |  |  | |
| 19 | Passing an empty string or null value for product_id, which will likely result in a validation error. |  |  |  | |
| 20 | This API returns inventory details only and is scoped to a single product per request. |  |  | 362: `return product` | |

## get_user_details

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Retrieves detailed information about a specific user, including their associated orders. |  |  | 394: `return user` | |
| 2 | Use this API when you need to look up a user's profile details or order history given their user ID. |  |  | 394: `return user` | |
| 3 | Do not use this API for searching users by name, email, or other attributes—it requires an exact user ID. |  |  | 394: `return user` | |
| 4 | Also do not use this API to modify user data; it is read-only. |  |  | 394: `return user` | |
| 5 | Parameters: - user_id (string, required): The unique identifier for the user to look up. |  |  | 394: `return user` | |
| 6 | This is a string value typically formatted as a combination of the user's name and a numeric suffix (e.g., a pattern like 'firstname_lastname_123'). |  |  | 394: `return user` | |
| 7 | The value must be a non-empty string and must exactly match an existing user's ID. |  |  | 394: `return user` | |
| 8 | Passing a null, empty, or incorrectly formatted user_id will likely result in a validation or not-found error. |  |  |  | |
| 9 | Ensure the user_id is obtained from a reliable source (such as a prior API response or known reference) to avoid lookup failures due to typos or incorrect identifiers. |  |  |  | |

## list_all_product_types

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Retrieves a list of all product types available in the store, returning each product type's name and product ID. |  |  |  | |
| 2 | The store contains exactly 50 product types. |  | POLICY: ### Product Our retail store has 50 types of products. |  | |
| 3 | Each product type encompasses multiple distinct items, each with unique item IDs and options; however, this API returns only the top-level product type information (name and product ID), not individual items or their options. |  |  |  | |
| 4 | When to use: Use this API when you need to discover or enumerate the available product types, look up a product type's name or ID, or obtain a complete catalog overview of product types. |  |  |  | |
| 5 | It is useful as a first step before querying for specific items or options within a particular product type. |  |  |  | |
| 6 | When NOT to use: Do not use this API if you already know the specific product type ID and need details about individual items, item options, or item-level information within that product type. |  |  |  | |
| 7 | This API does not accept filters, search queries, or pagination parameters, and it does not return item-level data. |  |  | 408: `return json.dumps(product_dict, sort_keys=True)` | |
| 8 | Parameters: This API takes no parameters. |  |  |  | |
| 9 | The request body should be an empty object. |  |  |  | |
| 10 | No filtering, sorting, or pagination is supported or needed, as the full set of 50 product types is always returned in its entirety. |  |  |  | |
| 11 | Validation: Since there are no parameters, validation failures are unlikely. |  |  |  | |
| 12 | Ensure that no unexpected parameters are passed, as the API accepts none. |  |  |  | |
| 13 | The call should be made with an empty parameter object. |  |  |  | |

## modify_pending_order_address

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Modifies the shipping address of an existing order that is currently in 'pending' status. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 438: `# Check if the order exists and is pending`<br>440: `if not self._is_pending_order(order):`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 2 | Use this API when a user requests to change or update the delivery address on an order that has not yet been shipped or processed. |  |  | 438: `# Check if the order exists and is pending`<br>440: `if not self._is_pending_order(order):`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 3 | Do NOT use this API for orders that are already shipped, delivered, cancelled, or in any non-pending state. |  |  | 438: `# Check if the order exists and is pending`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 4 | Do NOT use this API to modify other order details such as items, quantities, payment method, or shipping speed — it is exclusively for address changes. |  |  | 438: `# Check if the order exists and is pending`<br>440: `if not self._is_pending_order(order):`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 5 | Before calling this API, the agent must clearly explain the proposed address modification to the user and obtain explicit confirmation (yes/no) to proceed. |  |  |  | |
| 6 | Parameters (all required): - order_id (string, required): The unique identifier for the order. |  |  | 438: `# Check if the order exists and is pending`<br>440: `if not self._is_pending_order(order):`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 7 | Must include the '#' prefix followed by the order number (e.g., formatted as '#W' followed by digits). |  |  | 438: `# Check if the order exists and is pending`<br>440: `if not self._is_pending_order(order):`<br>441: `raise ValueError("Non-pending order cannot be modified")` | |
| 8 | Omitting the '#' prefix will likely cause a validation failure. |  |  |  | |
| 9 | - address1 (string, required): The primary street address line (e.g., street number and name). |  |  |  | |
| 10 | Must not be empty. |  |  |  | |
| 11 | - address2 (string, required): The secondary address line for additional details such as apartment, suite, or unit number. |  |  |  | |
| 12 | If there is no secondary address information, provide an empty string. |  |  |  | |
| 13 | Do not omit this parameter. |  |  |  | |
| 14 | - city (string, required): The city name for the shipping address. |  |  |  | |
| 15 | - state (string, required): The state or region abbreviation for the shipping address (e.g., two-letter state code for US addresses). |  |  |  | |
| 16 | - country (string, required): The country for the shipping address (e.g., 'USA'). |  |  |  | |
| 17 | - zip (string, required): The postal/zip code for the shipping address. |  |  |  | |
| 18 | Provided as a string, not a number. |  |  |  | |
| 19 | All seven parameters must be supplied together as a complete address. |  |  |  | |
| 20 | Partial address updates are not supported — even if only one field is changing, the full address must be provided. |  |  |  | |
| 21 | Ensure all address fields are internally consistent (e.g., the city, state, zip, and country should correspond to a valid real-world location). |  |  |  | |
| 22 | Common mistakes include omitting the '#' prefix on order_id, leaving out the address2 field instead of passing an empty string, and providing an incomplete set of address fields. |  |  |  | |

## modify_pending_order_items

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Modify one or more items in a pending order by swapping them for different variants of the same product. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 2 | This API is used when a user wants to change specific items in an order that has not yet been processed (i.e., the order status is 'pending'). |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 3 | It should NOT be used for orders that are already shipped, delivered, cancelled, or in any non-pending state. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 4 | It should NOT be used to add entirely new products, remove items, or change quantities—only to swap existing items for alternative variants of the same product (e.g., changing size or color). |  |  | 485: `# Check if the items to be modified exist. There can be dupl`<br>493: `raise ValueError("The number of items to be exchanged should`<br>501: `item = next((item for item in order.items if item.item_id ==` | |
| 5 | This function can only be called once per pending order; subsequent modification attempts on the same order will fail. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 6 | Before calling this API, the agent must explain the exchange details (including any price difference) to the user and obtain explicit confirmation (yes/no) to proceed. |  | POLICY: Before taking any action that updates the database (cancel, modify, return, exch |  | |
| 7 | Parameters (all required): 1. |  |  |  | |
| 8 | order_id (string, required): The unique identifier of the order to modify. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 9 | Must include the '#' prefix followed by the order number (e.g., formatted as '#W' followed by digits). |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 10 | Omitting the '#' prefix will likely cause a validation failure. |  |  |  | |
| 11 | 2. |  |  |  | |
| 12 | item_ids (array of strings, required): A list of item IDs currently in the order that the user wants to replace. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 13 | Each item ID is a numeric string. |  |  | 501: `item = next((item for item in order.items if item.item_id ==`<br>502: `if item is None:`<br>503: `raise ValueError(f"Item {item_id} not found")` | |
| 14 | Duplicate entries are allowed if the order contains multiple units of the same item that all need modification. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 15 | Every item ID listed must exist in the specified order. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 16 | 3. |  |  |  | |
| 17 | new_item_ids (array of strings, required): A list of replacement item IDs, positionally matched to item_ids. |  |  | 485: `# Check if the items to be modified exist. There can be dupl`<br>488: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>492: `if len(item_ids) != len(new_item_ids):` | |
| 18 | Each new item ID must correspond to a variant of the same product as the item it replaces (at the same array index). |  |  | 501: `item = next((item for item in order.items if item.item_id ==`<br>502: `if item is None:`<br>503: `raise ValueError(f"Item {item_id} not found")` | |
| 19 | The array must be the same length as item_ids. |  |  | 488: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>492: `if len(item_ids) != len(new_item_ids):` | |
| 20 | Duplicates are allowed. |  |  |  | |
| 21 | Providing a new item ID that belongs to a different product than the original item at that position will cause a failure. |  |  | 501: `item = next((item for item in order.items if item.item_id ==`<br>502: `if item is None:`<br>503: `raise ValueError(f"Item {item_id} not found")` | |
| 22 | 4. |  |  |  | |
| 23 | payment_method_id (string, required): The payment method to use for charging or refunding any price difference resulting from the item swap. |  |  | 501: `item = next((item for item in order.items if item.item_id ==`<br>502: `if item is None:`<br>503: `raise ValueError(f"Item {item_id} not found")` | |
| 24 | Must be a valid payment method ID associated with the user or the order, typically formatted as 'gift_card_' or 'credit_card_' followed by digits. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 25 | This can be looked up from user account details or order details. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 26 | Common mistakes to avoid: - Forgetting the '#' prefix on order_id. |  |  |  | |
| 27 | - Mismatching the lengths of item_ids and new_item_ids arrays. |  |  | 488: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>492: `if len(item_ids) != len(new_item_ids):` | |
| 28 | - Pairing a new_item_id with an original item_id from a different product category. |  |  | 488: `if item_ids.count(item_id) > all_item_ids.count(item_id):`<br>489: `raise ValueError(f"{item_id} not found")`<br>497: `if item_id == new_item_id:` | |
| 29 | - Attempting to call this API more than once on the same order. |  |  | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 30 | - Calling this API on an order that is not in pending status. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 480: `# Check if the order exists and is pending`<br>482: `if order.status != "pending":`<br>483: `raise ValueError("Non-pending order cannot be modified")` | |
| 31 | - Proceeding without first explaining the modification details and receiving explicit user confirmation. |  |  |  | |

## modify_pending_order_payment

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Modifies the payment method associated with a pending order. |  | POLICY: For a pending order, you can take actions to modify its shipping address, paymen | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 2 | Use this API when a user wants to change how they are paying for an order that has not yet been processed (i.e., the order is still in a 'pending' state). |  |  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 3 | Do NOT use this API for orders that have already been delivered, shipped, cancelled, or otherwise moved beyond the pending stage. |  |  | 567: `# Check if the order exists and is pending`<br>569: `raise ValueError("Non-pending order cannot be modified")`<br>579: `raise ValueError("There should be exactly one payment for a ` | |
| 4 | Do NOT use this API to modify other aspects of the order such as items, quantities, or shipping details—it only changes the payment method. |  |  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 5 | Before calling this API, the agent must clearly explain the modification details to the user (specifically which order and which new payment method will be applied) and obtain explicit user confirmation (yes/no) before proceeding. |  |  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 6 | Parameters: 1. |  |  |  | |
| 7 | **order_id** (string, required): The unique identifier of the pending order to modify. |  |  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 8 | This value must begin with the '#' character followed by a 'W' and digits (e.g., formatted like '#W' followed by seven digits). |  |  |  | |
| 9 | A common mistake is omitting the leading '#' symbol, which will cause validation failure. |  |  |  | |
| 10 | The order must exist and must be in a pending state. |  | POLICY: ### Order Each order has the following attributes: - unique order id - user id - | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 11 | 2. |  |  |  | |
| 12 | **payment_method_id** (string, required): The identifier of the payment method to assign to the order. |  |  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 13 | This value follows a pattern such as 'gift_card_' or 'credit_card_' followed by a numeric identifier. |  |  |  | |
| 14 | The payment method must belong to the user who owns the order. |  | POLICY: After user confirmation, the order status will be changed to 'cancelled', and th | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 15 | This can be looked up from the user's profile or from existing order details. |  | POLICY: Once the user has been authenticated, you can provide the user with information  | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 16 | Using a payment method ID that does not belong to the user or does not exist will result in a validation failure. |  |  | 571: `# Check if the payment method exists`<br>579: `raise ValueError("There should be exactly one payment for a `<br>589: `# Check if the new payment method has enough balance if it i` | |
| 17 | Common validation failures and how to avoid them: - Ensure the order_id includes the '#' prefix. |  |  |  | |
| 18 | - Ensure the order is still in pending status before attempting modification. |  | POLICY: ## Cancel pending order An order can only be cancelled if its status is 'pending | 567: `# Check if the order exists and is pending`<br>568: `if not self._is_pending_order(order):`<br>569: `raise ValueError("Non-pending order cannot be modified")` | |
| 19 | - Ensure the payment_method_id references a valid payment method associated with the user. |  |  | 571: `# Check if the payment method exists`<br>579: `raise ValueError("There should be exactly one payment for a `<br>582: `if order.payment_history[0].payment_method_id == payment_met` | |
| 20 | - Both parameters are required; omitting either will cause the call to fail. |  |  |  | |
| 21 | - Do not proceed without first obtaining explicit user confirmation after explaining the intended change. |  |  |  | |

## modify_user_address

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Updates the default address on file for a specified user. |  | POLICY: # Retail agent policy As a retail agent, you can help users: - **cancel or modif | 661: `return user` | |
| 2 | Use this API when a user requests a change to their default shipping or billing address. |  |  | 661: `return user` | |
| 3 | Do not use this API for creating new users, adding secondary/non-default addresses, or modifying any user profile information other than the default address. |  |  | 661: `return user` | |
| 4 | Before calling this API, the agent must clearly summarize the proposed address modification to the user and obtain explicit confirmation (yes/no) to proceed; do not call this API without that confirmation. |  |  | 661: `return user` | |
| 5 | Parameters: - user_id (string, required): The unique identifier for the user whose address is being modified. |  |  | 661: `return user` | |
| 6 | Follows a name-based format with underscores and a numeric suffix (e.g., lowercase first_last_digits pattern). |  |  |  | |
| 7 | Must correspond to an existing user; an invalid or nonexistent user_id will cause the request to fail. |  |  | 661: `return user` | |
| 8 | - address1 (string, required): The primary street address line (e.g., street number and name). |  |  |  | |
| 9 | Must not be empty; this is the main locator for the address. |  |  |  | |
| 10 | - address2 (string, required): The secondary address line for additional location details such as apartment, suite, or unit number. |  |  |  | |
| 11 | If there is no secondary address information, pass an empty string. |  |  |  | |
| 12 | Do not omit this parameter. |  |  |  | |
| 13 | - city (string, required): The city name for the address. |  |  |  | |
| 14 | Must not be empty. |  |  |  | |
| 15 | - state (string, required): The state or province abbreviation (e.g., two-letter code for US states). |  |  |  | |
| 16 | Must not be empty and should match the conventions of the specified country. |  |  |  | |
| 17 | - country (string, required): The country for the address (e.g., standard country name or code). |  |  |  | |
| 18 | Must not be empty and should be consistent with the state and zip values provided. |  |  |  | |
| 19 | - zip (string, required): The postal/zip code for the address. |  |  |  | |
| 20 | Provided as a string to preserve leading zeros and support international formats. |  |  |  | |
| 21 | Must not be empty and should be valid for the given country and state. |  |  |  | |
| 22 | All seven parameters are required; omitting any parameter will result in a validation failure. |  |  |  | |
| 23 | The address fields (address1, city, state, country, zip) should be internally consistent—state should be a valid subdivision of the specified country, and zip should be a valid postal code for the given state and country. |  |  |  | |
| 24 | Common mistakes include omitting address2 instead of passing an empty string, providing a user_id that does not exist, or supplying mismatched geographic values (e.g., a zip code that does not correspond to the given city/state). |  |  |  | |
| 25 | This API replaces the entire default address; all fields are overwritten, so every field must contain the correct final value, not just the fields being changed. |  |  |  | |

## return_delivered_order_items

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Initiates a return request for one or more items from an order that has already been delivered. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 2 | Use this API when a customer wants to return specific items from a delivered order. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 3 | Do not use this API for orders that have not yet been delivered, for cancellations, for exchanges, or for returning entire orders without specifying individual item IDs. |  |  | 673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292`<br>690: `if order.status != "delivered":` | |
| 4 | Upon successful invocation, the order status changes to 'return requested', and the customer will receive a follow-up email with instructions on how and where to return the items. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 5 | Before calling this API, the agent must clearly explain the return details to the user and obtain explicit confirmation (yes/no) to proceed. |  | POLICY: Before taking any action that updates the database (cancel, modify, return, exch | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 6 | Parameters: - order_id (string, required): The unique identifier for the order. |  |  | 671: `The order status will be changed to 'return requested'.`<br>682: `Order: The order details after requesting the return.`<br>690: `if order.status != "delivered":` | |
| 7 | Must begin with the '#' character followed by the order number (e.g., formatted as '#W' followed by digits). |  |  | 671: `The order status will be changed to 'return requested'.`<br>682: `Order: The order details after requesting the return.`<br>690: `if order.status != "delivered":` | |
| 8 | A common mistake is omitting the leading '#' symbol, which will cause validation failure. |  |  |  | |
| 9 | - item_ids (array of strings, required): A list of item identifiers to be returned from the order. |  |  | 671: `The order status will be changed to 'return requested'.`<br>673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292` | |
| 10 | Each item ID is a string representing a numeric identifier. |  |  | 673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292`<br>707: `raise ValueError("Some item not found")` | |
| 11 | The list must contain at least one item ID. |  | POLICY: Each product has the following attributes: - unique product id - name - list of  | 673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292`<br>703: `# Check if the items to be returned exist (there could be du` | |
| 12 | Duplicate item IDs are permitted in the list, which accounts for cases where the order contains multiple units of the same item. |  |  | 671: `The order status will be changed to 'return requested'.`<br>673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292` | |
| 13 | Each item ID must correspond to an item that exists within the specified order; providing an item ID not belonging to the order will likely cause a validation error. |  |  | 671: `The order status will be changed to 'return requested'.`<br>673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292` | |
| 14 | - payment_method_id (string, required): The payment method to be used for processing the refund for the returned items. |  |  | 677: `item_ids: The item ids to be returned, each such as '1008292`<br>687: `ValueError: If the items to be returned do not exist.`<br>691: `raise ValueError("Non-delivered order cannot be returned")` | |
| 15 | This should reference an existing payment method associated with the user or the order, such as a gift card or credit card identifier. |  | POLICY: After user confirmation, the order status will be changed to 'cancelled', and th | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 16 | Valid formats follow patterns like 'gift_card_' or 'credit_card_' followed by a numeric identifier. |  |  | 673: `The user will receive follow-up email for how and where to r` | |
| 17 | This value can be looked up from the user's account details or the order details. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 18 | Providing an invalid or non-existent payment method ID will result in a failure. |  |  | 693: `# Check if the payment method exists and is either the origi`<br>701: `raise ValueError("Payment method should be the original paym` | |
| 19 | Validation and common pitfalls: - All three parameters are required; omitting any one will result in an error. |  |  |  | |
| 20 | - The order must be in a delivered state; attempting to return items from an order in any other status will likely fail. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |
| 21 | - Ensure item IDs are provided as strings, not integers. |  |  | 673: `The user will receive follow-up email for how and where to r`<br>677: `item_ids: The item ids to be returned, each such as '1008292`<br>707: `raise ValueError("Some item not found")` | |
| 22 | - The payment method must be one that is valid and accessible for the user in question. |  | POLICY: After user confirmation, the order status will be changed to 'cancelled', and th | 672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r`<br>693: `# Check if the payment method exists and is either the origi` | |
| 23 | - Cross-parameter dependency: the item_ids must all belong to the order specified by order_id, and the payment_method_id must be a valid method associated with the user or that order. |  |  | 671: `The order status will be changed to 'return requested'.`<br>672: `The agent needs to explain the return detail and ask for exp`<br>673: `The user will receive follow-up email for how and where to r` | |

## transfer_to_human_agents

| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |
|---|---|---|---|---|---|
| 1 | Transfers the current conversation to a human agent. |  |  |  | |
| 2 | Use this API only when one of the following conditions is met: (1) the user has explicitly requested to speak with a human agent, or (2) the user's issue cannot be resolved using the available tools and policies at your disposal. |  |  |  | |
| 3 | Do NOT use this API if you are still able to address the user's request through other available tools or if the user has not asked for a human agent. |  |  |  | |
| 4 | This API requires a single parameter: 'summary' (string, required), which must contain a concise summary of the user's issue up to this point in the conversation. |  |  |  | |
| 5 | The summary should accurately capture the nature of the problem, any relevant details the user has provided, and any steps already attempted, so the human agent can continue without requiring the user to repeat themselves. |  |  |  | |
| 6 | The 'summary' parameter must be a non-empty string; omitting it or passing a null or empty value will result in a validation failure. |  |  |  | |
| 7 | Since this is the only parameter and it is required, every call must include it. |  |  |  | |
| 8 | Avoid vague or overly brief summaries that would leave the human agent without sufficient context to assist the user. |  |  |  | |
