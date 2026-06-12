# JSON2CSV
A hobby project to convert Json to csv and excel

## Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd JSON2CSV
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project

1. Prepare your JSON input file

2. Run the converter:
   ```bash
   python json2csv.py --input <input.json> --output <output.csv>
   ```

3. The converted CSV/Excel file will be generated in the output directory

### Example Usage

```bash
python json2csv.py --input data.json --output data.csv
```

