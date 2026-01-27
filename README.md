# Project Prioritization & Scoring System

Professional digitalization project scoring system for compliance and ethical review.

## Features

- ✅ Multi-criteria scoring (7 dimensions)
- ✅ Automated priority assignment
- ✅ Compliance officer review workflow
- ✅ Override capabilities with audit trail
- ✅ Real-time analytics dashboard
- ✅ Red flag detection
- ✅ Export to CSV/Excel

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.9+
- **Database:** SQLite
- **Charts:** Plotly
- **Hosting:** Streamlit Cloud (free)

## Quick Start

### Local Development

1. Clone repository:
```bash
git clone https://github.com/YOUR_USERNAME/project-scoring-system.git
cd project-scoring-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run application:
```bash
streamlit run app.py
```

4. Open browser: `http://localhost:8501`

### Demo Credentials

**Requestor:**
- Username: `requestor`
- Password: `req123`

**Compliance Officer:**
- Username: `admin`
- Password: `admin123`

## Deployment to Streamlit Cloud

See DEPLOYMENT.md for step-by-step instructions.

## Scoring Methodology

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Regulatory Risk | 25% | Compliance deadlines, enforcement |
| Reputational Risk | 20% | Stakeholder harm, liability |
| Strategic Alignment | 15% | Corporate strategy linkage |
| Operational Impact | 15% | Efficiency gains, scope |
| Resource Requirements | 10% | Time, budget, complexity |
| Data Sensitivity | 10% | GDPR, confidentiality |
| Stakeholder Pressure | 5% | Executive/external demands |

**Priority Thresholds:**
- 🔴 IMMEDIATE: ≥70 points
- 🟡 PLANNED: 50-69 points
- ⚪ DEFER: <50 points

## Project Structure
```
project-scoring-system/
├── app.py                  # Main entry point
├── pages/
│   ├── 1_📝_New_Request.py    # Submission form
│   ├── 2_⚖️_Review_Queue.py   # Compliance review
│   ├── 3_📊_Dashboard.py      # Analytics
│   └── 4_⚙️_Admin.py          # Configuration
├── utils/
│   ├── database.py         # SQLite operations
│   ├── scoring.py          # Calculation logic
│   └── auth.py             # Authentication
├── requirements.txt
└── README.md
```

## Customization

### Change Scoring Weights

Edit `utils/scoring.py` → `calculate_total_score()` function

### Add Departments

Edit department lists in:
- `pages/1_📝_New_Request.py`
- `utils/database.py`

### Modify Thresholds

Edit `utils/scoring.py` → `get_priority()` function

## Security Notes

⚠️ **Current implementation uses simple auth for demo purposes.**

For production:
- Implement proper authentication (OAuth, SAML)
- Use PostgreSQL instead of SQLite
- Add HTTPS/SSL
- Implement role-based access control (RBAC)
- Add audit logging
- Secure secrets management

## License

MIT License - feel free to adapt for your organization

## Support

For issues: Open GitHub issue
For questions: Contact compliance team
