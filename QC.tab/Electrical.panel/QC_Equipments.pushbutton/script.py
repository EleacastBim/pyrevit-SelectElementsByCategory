# -*- coding: utf-8 -*-
import clr
import os

# Cargar ensamblados básicos de WPF
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from pyrevit import revit, DB, script, forms

class ElementData(object):
    def __init__(self, element):
        self.Id = element.Id.IntegerValue
        self.Name = element.Name

class QCWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        # Ruta absoluta al XAML
        xaml_path = os.path.join(os.path.dirname(__file__), xaml_file_name)
        forms.WPFWindow.__init__(self, xaml_path)
        self.Title = "QC Equipments" 
        self._setup_categories()

    def _setup_categories(self):
        try:
            doc = revit.doc
            collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType()
            
            categories = set()
            for el in collector:
                if el.Category:
                    categories.add(el.Category.Name)
            
            self.category_cb.ItemsSource = sorted(list(categories))
        except Exception as e:
            print("Error poblando categorias: {}".format(e))

    def category_changed(self, sender, args):
        try:
            doc = revit.doc
            category_name = self.category_cb.SelectedItem
            if not category_name:
                return

            all_categories = doc.Settings.Categories
            target_category = None
            for cat in all_categories:
                if cat.Name == category_name:
                    target_category = cat
                    break
            
            if target_category:
                collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategoryId(target_category.Id).WhereElementIsNotElementType()
                elements = [ElementData(el) for el in collector]
                self.elements_dg.ItemsSource = elements
        except Exception as e:
            print("Error al cambiar categoria: {}".format(e))

    def select_click(self, sender, args):
        try:
            selected_items = self.elements_dg.SelectedItems
            if not selected_items:
                forms.alert("No elements selected in the list.")
                return

            element_ids = []
            for item in selected_items:
                element_ids.append(DB.ElementId(item.Id))
            
            from System.Collections.Generic import List
            id_list = List[DB.ElementId](element_ids)
            
            revit.uidoc.Selection.SetElementIds(id_list)
            revit.uidoc.ShowElements(id_list)
        except Exception as e:
            forms.alert("Error al seleccionar elementos: {}".format(e))

def main():
    try:
        # Intentar mostrar la ventana personalizada
        ui = QCWindow("ui.xaml")
        ui.show()
    except Exception as e:
        # Fallback en caso de que la UI personalizada falle totalmente
        print("La UI personalizada no pudo cargar: {}".format(e))
        print("Intentando modo simplificado...")
        
        doc = revit.doc
        # Obtener categorias disponibles
        collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType()
        cats = sorted(list(set([el.Category.Name for el in collector if el.Category])))
        
        sel_cat = forms.SelectFromList.show(cats, title="Seleccionar Categoria (Modo Seguro)", multiselect=False)
        
        if sel_cat:
            target_cat = next((c for c in doc.Settings.Categories if c.Name == sel_cat), None)
            if target_cat:
                els = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategoryId(target_cat.Id).WhereElementIsNotElementType().ToElements()
                from pyrevit import forms
                forms.select_elements(els)

if __name__ == "__main__":
    main()
