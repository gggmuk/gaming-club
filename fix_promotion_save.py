"""
Script to fix operations_dashboard.html - specifically the submitPromotion function
and ensure proper error handling for API calls.
"""

import re

# Read the file
with open(r'c:\codes\вкр\templates\operations_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the submitPromotion function to add better error handling
new_submit_promotion = '''        async function submitPromotion() {
            const id = document.getElementById('promotionId').value;
            const data = {
                name: document.getElementById('promotionName').value,
                discount_percentage: document.getElementById('promotionDiscount').value,
                description: document.getElementById('promotionDesc').value,
                is_active: document.getElementById('promotionActive').checked
            };

            const url = id ? `/api/promotions/${id}/` : '/api/promotions/';
            const method = id ? 'PUT' : 'POST';

            try {
                const res = await fetch(url, {
                    method: method,
                    headers: { 
                        'Content-Type': 'application/json', 
                        'X-CSRFToken': getCookie('csrftoken') 
                    },
                    body: JSON.stringify(data)
                });
                
                if (res.ok) {
                    closeModal('promotionModal');
                    loadManagement();
                    alert('Акция успешно сохранена!');
                } else {
                    const errorData = await res.json();
                    console.error('Promotion save error:', errorData);
                    alert('Ошибка сохранения: ' + JSON.stringify(errorData));
                }
            } catch (e) { 
                console.error('Promotion save exception:', e); 
                alert('Ошибка соединения: ' + e.message);
            }
        }'''

# Use regex to find and replace the submitPromotion function
pattern = r'async function submitPromotion\(\) \{[^}]*\}(?:\s*\})*'
content = re.sub(pattern, new_submit_promotion, content, flags=re.DOTALL)

# Write back
with open(r'c:\codes\вкр\templates\operations_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed submitPromotion function with better error handling")
print("Now check the browser console for detailed error messages when saving promotions")
