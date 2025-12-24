from pyrevit import revit, DB, script, forms
import clr

class ElementData(object):
    def __init__(self, element):
        self.Id = element.Id.IntegerValue
        self.Name = element.Name
        self.Element = element

class QCWindow(forms.WPFWindow):
    def __init__(self, xaml_file_name):
        forms.WPFWindow.__init__(self, xaml_file_name)
        self._setup_categories()

    def _setup_categories(self):
        doc = revit.doc
        # Get categories of all elements in active view to populate dropdown
        collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType()
        
        categories = set()
        for el in collector:
            if el.Category:
                categories.add(el.Category.Name)
        
        self.category_cb.ItemsSource = sorted(list(categories))

    def category_changed(self, sender, args):
        doc = revit.doc
        category_name = self.category_cb.SelectedItem
        if not category_name:
            return

        # Find BuiltInCategory from Name (simplified for this task)
        # Better: Filter by category name directly in collector or find the category object
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

    def select_click(self, sender, args):
        selected_items = self.elements_dg.SelectedItems
        if not selected_items:
            forms.alert("No elements selected in the list.")
            return

        element_ids = [DB.ElementId(item.Id) for item in selected_items]
        
        from System.Collections.Generic import List
        id_list = List[DB.ElementId](element_ids)
        
        revit.uidoc.Selection.SetElementIds(id_list)
        revit.uidoc.ShowElements(id_list)

def main():
    QCWindow("ui.xaml").show()

if __name__ == "__main__":
    main()

