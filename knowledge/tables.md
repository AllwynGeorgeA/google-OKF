# Tables (DEMO DATA, SQLite)

## orders
| column | type | note |
|---|---|---|
| id | INTEGER PK | |
| created_at | TEXT | 'YYYY-MM-DD HH:MM:SS' |
| amount | REAL | order value |
| status | TEXT | 'paid' or 'unpaid' |
| channel | TEXT | 'web' or 'app' |

## payment_attempts
| column | type | note |
|---|---|---|
| id | INTEGER PK | |
| order_id | INTEGER | references orders.id |
| created_at | TEXT | 'YYYY-MM-DD HH:MM:SS' |
| status | TEXT | 'success' or 'failed' |
| failure_reason | TEXT | NULL when success |
| payment_method | TEXT | 'card', 'wallet', 'bank_transfer' |
