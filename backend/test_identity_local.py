import sys
sys.path.append('c:\\Users\\Dell\\Desktop\\unihack-product-intelligence\\backend')
from app.services.identity import identity_resolver
from app.schemas.schemas import ProductRow

print('Testing DDG and Google Search fallback')
query = '"DCB518ASTS06G"'
print('Strict query:', query)
print(identity_resolver._search(query))

row = ProductRow(row_id=1, mfg_part_num='DCB518ASTS06G', part_desc='DCB518ASTS06G', part_manuf='GE')
res = identity_resolver.resolve(row)
print(f'Status: {res.status}, URL: {res.official_source_url}')
