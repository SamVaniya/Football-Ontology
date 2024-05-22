import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, messagebox, scrolledtext, ttk
from rdflib import Graph, RDF, OWL
from owlready2 import get_ontology, sync_reasoner_pellet
import io
import sys

def load_ontology(file_path):
    g = Graph()
    g.parse(file_path, format="xml")
    return g

def produce_formatted_output(graph):
    return graph.serialize(format="turtle")

def invoke_reasoner(file_path, text_widget):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = mystdout = io.StringIO()
    sys.stderr = mystderr = io.StringIO()
    try:
        onto = get_ontology(file_path).load()
        with onto:
            sync_reasoner_pellet()
            print(onto)
        return onto
    except Exception as e:
        raise e
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        reasoner_output = mystdout.getvalue() + mystderr.getvalue()
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, reasoner_output)

def execute_sparql_query(graph, query):
    qres = graph.query(query)
    return qres

def display_results(results, text_widget):
    text_widget.delete(1.0, tk.END)
    if results:
        max_uri_width = max(len(str(row[0])) for row in results)
        text_widget.insert(tk.END, f"{'URI'.ljust(max_uri_width)}\tLiteral\n")
        text_widget.insert(tk.END, f"{'-'*max_uri_width}\t{'-'*len('Literal')}\n")
        for row in results:
            uri = str(row[0])
            literal = str(row[1]) if len(row) > 1 else ''
            text_widget.insert(tk.END, f"{uri.ljust(max_uri_width)}\t{literal}\n")
    else:
        text_widget.insert(tk.END, "No results found.\n")

def display_triples(graph, text_widget):
    text_widget.delete(1.0, tk.END)
    for subj, pred, obj in graph:
        text_widget.insert(tk.END, f"Subject : {subj} --> Predicate : {pred} --> Object : {obj}\n\n")

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("OWL files", "*.owl"), ("RDF/XML files", "*.rdf"), ("All files", "*.*")])
    if file_path:
        try:
            global ontology_graph
            ontology_graph = load_ontology(file_path)
            populate_class_dropdown(ontology_graph)
            messagebox.showinfo("Success", "Ontology loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ontology: {e}")

def show_formatted_output():
    if ontology_graph:
        formatted_output = produce_formatted_output(ontology_graph)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, formatted_output)
    else:
        messagebox.showwarning("Warning", "Load an ontology first")

def apply_reasoner():
    file_path = filedialog.askopenfilename(filetypes=[("OWL files", "*.owl"), ("All files", "*.*")])
    if file_path:
        try:
            global ontology_with_reasoning
            ontology_with_reasoning = invoke_reasoner(file_path, text_output)
            messagebox.showinfo("Success", "Reasoning applied successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply reasoner: {e}")

def run_sparql_query():
    query = query_text.get(1.0, tk.END).strip()
    if query and ontology_graph:
        try:
            query_results = execute_sparql_query(ontology_graph, query)
            text_output.delete(1.0, tk.END)
            display_results(query_results, text_output)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {e}")
    else:
        messagebox.showwarning("Warning", "Load an ontology and enter a query first")

def reset_fields():
    query_text.delete(1.0, tk.END)
    text_output.delete(1.0, tk.END)

def populate_class_dropdown(graph):
    query = """
    SELECT DISTINCT ?class
    WHERE {
        ?instance a ?class .
        ?class a owl:Class .
    }
    """
    results = execute_sparql_query(graph, query)
    classes_with_instances = sorted(set(row[0].split('#')[-1] if '#' in row[0] else row[0].split('/')[-1] for row in results))
    
    class_dropdown['values'] = classes_with_instances
    if classes_with_instances:
        class_dropdown.current(0)
        display_class_members()

def display_class_members(event=None):
    selected_class = class_dropdown.get()
    if not selected_class:
        messagebox.showwarning("Warning", "No class selected.")
        return
    
    query = f"""
    SELECT ?instance
    WHERE {{
        ?instance a <http://www.semanticweb.org/lenovo/ontologies/2024/4/Football#{selected_class}> .
    }}
    """
    
    if ontology_graph:
        try:
            query_results = execute_sparql_query(ontology_graph, query)
            display_results(query_results, text_output)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {e}")
    else:
        messagebox.showwarning("Warning", "Load an ontology first.")

# Main application window
app = tk.Tk()
app.title("Ontology Processor")
app.geometry("1000x800")

# Define a bold font
bold_font = tkFont.Font(family="Helvetica", size=16, weight="bold")

# Frame for file operations
frame_file = tk.Frame(app)
frame_file.pack(pady=10)

btn_load = tk.Button(frame_file, text="Load Ontology", command=load_file, font=bold_font)
btn_load.pack(side=tk.LEFT, padx=5)

btn_reasoner = tk.Button(frame_file, text="Apply Reasoner", command=apply_reasoner, font=bold_font)
btn_reasoner.pack(side=tk.LEFT, padx=5)

btn_output = tk.Button(frame_file, text="Show Formatted Output", command=show_formatted_output, font=bold_font)
btn_output.pack(side=tk.LEFT, padx=5)

btn_triples = tk.Button(frame_file, text="Show Triples", command=lambda: display_triples(ontology_graph, text_output), font=bold_font)
btn_triples.pack(side=tk.LEFT, padx=5)

# Frame for class selection
frame_class = tk.Frame(app)
frame_class.pack(pady=10)

class_label = tk.Label(frame_class, text="Get Info Of :", font=bold_font)
class_label.pack(side=tk.LEFT, padx=5)

class_dropdown = ttk.Combobox(frame_class, font=bold_font)
class_dropdown.pack(side=tk.LEFT, padx=5)
class_dropdown.bind("<<ComboboxSelected>>", display_class_members)

# Text area for SPARQL query input
query_label = tk.Label(app, text="Enter SPARQL Query:", font=bold_font)
query_label.pack(pady=5)

query_text = scrolledtext.ScrolledText(app, height=5, width=150, font=bold_font)
query_text.pack(pady=5)

btn_query = tk.Button(app, text="Run Query", command=run_sparql_query, font=bold_font)
btn_query.pack(pady=5)

# Reset Button
btn_reset = tk.Button(app, text="Reset", command=reset_fields, font=bold_font)
btn_reset.pack(pady=5)

# Text area for Output
output_label = tk.Label(app, text="Output Text Area:", font=bold_font)
output_label.pack(pady=5)

# Text area for displaying results
text_output = scrolledtext.ScrolledText(app, height=20, width=150, font=bold_font)
text_output.pack(pady=5)

# Global variables to hold ontology data
ontology_graph = None
ontology_with_reasoning = None  

# Run the application
app.mainloop()
