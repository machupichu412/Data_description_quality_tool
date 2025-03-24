# Data Description Quality Guidelines

## Overview
High-quality data descriptions are essential for data understanding, governance, and utilization. These guidelines outline the criteria for evaluating data descriptions.

## Quality Criteria

### 1. Clarity
- Descriptions should be clear and unambiguous
- Avoid technical jargon unless necessary
- Define acronyms and specialized terms
- Use simple, direct language

### 2. Completeness
- Include the purpose of the data
- Specify the data source or collection method
- Mention the update frequency if applicable
- Include any relevant units of measurement
- Document any data transformations

### 3. Accuracy
- Description must match the actual data content
- Avoid misleading statements
- Ensure numerical ranges or categories are correct
- Reference correct business context

### 4. Consistency
- Use consistent terminology throughout
- Maintain consistent level of detail
- Follow organizational naming conventions
- Ensure description aligns with related data elements

### 5. Relevance
- Focus on aspects that matter to data users
- Include business context
- Highlight important characteristics
- Mention limitations or caveats

## Examples

### Good Descriptions:
- "Customer Acquisition Date (YYYY-MM-DD): The date when the customer first purchased a product or service from our company."
- "Monthly Revenue (USD): Total revenue generated each month, calculated by summing all completed sales transactions. Updated on the first day of each month."
- "Product Category: Classification of products into hierarchical categories following the company's standard product taxonomy (Electronics, Clothing, Home Goods, etc.)."

### Poor Descriptions:
- "Date field" (too vague, lacks purpose and format)
- "The data" (completely uninformative)
- "Number of items in system from the process" (ambiguous, lacks specifics)
- "Code values for the thing" (lacks specifics about what the codes represent)
- "This field was added by John" (focuses on irrelevant information)

## Pass/Fail Criteria

A data description passes quality review if it:
- Is clear and understandable to the target audience
- Contains sufficient detail for proper data usage
- Accurately represents the data
- Is consistent with organizational standards
- Provides relevant business context

A data description fails quality review if it:
- Is vague, ambiguous, or confusing
- Lacks essential information
- Contains inaccuracies
- Uses inconsistent terminology
- Focuses on irrelevant details or omits important context
