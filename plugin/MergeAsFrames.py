import nanome
from nanome.util import async_callback, enums, ComplexUtils, Logs


class MergeAsFrames(nanome.AsyncPluginInstance):
    def start(self):
        self.set_plugin_list_button(enums.PluginListButtonType.run, 'Merge')
        self.set_plugin_list_button(enums.PluginListButtonType.advanced_settings, 'Settings')
        self.align_coordinates = False
        self.delete_originals = False
        self.create_settings_menu()

    def create_settings_menu(self):
        menu = nanome.ui.Menu()
        self.menu = menu

        menu.title = 'Settings'
        menu.width = 0.5
        menu.height = 0.2

        menu.root.padding_type = menu.root.PaddingTypes.ratio
        menu.root.set_padding(top=0.15, down=0.15, left=0.05, right=0.05)

        def toggle_align(btn):
            self.align_coordinates = btn.selected

        ln = menu.root.create_child_node()
        ln.set_padding(top=0.01, down=0.01)
        ln.forward_dist = 0.001
        self.btn_align = ln.add_new_toggle_switch('Align Coordinates')
        self.btn_align.register_pressed_callback(toggle_align)

        def toggle_delete(btn):
            self.delete_originals = btn.selected

        ln = menu.root.create_child_node()
        ln.set_padding(top=0.01, down=0.01)
        ln.forward_dist = 0.001
        self.btn_delete = ln.add_new_toggle_switch('Delete Entries')
        self.btn_delete.register_pressed_callback(toggle_delete)

    def on_advanced_settings(self):
        self.menu.enabled = True
        self.update_menu(self.menu)

    @async_callback
    async def on_run(self):
        shallow = await self.request_complex_list()
        indices_selected = [c.index for c in shallow if c.get_selected()]

        if len(indices_selected) < 2:
            self.send_notification(enums.NotificationTypes.warning, 'Please select multiple entries.')
            return

        complexes = await self.request_complexes(indices_selected)

        new_complex = nanome.structure.Complex()
        new_complex.position = complexes[0].position
        new_complex.rotation = complexes[0].rotation
        new_complex.name = 'Merged ' + complexes[0].name

        for i, complex in enumerate(complexes):
            complex = complex.convert_to_frames()
            complex.set_all_selected(False)
            if self.align_coordinates and i > 0:
                ComplexUtils.align_to(complex, complexes[0])
            for molecule in complex.molecules:
                new_complex.add_molecule(molecule)

        self.add_to_workspace([new_complex])

        if self.delete_originals:
            self.remove_from_workspace(complexes)


def main():
    desc = "A Nanome plugin to merge multiple entry list small molecule ligands into a single entry with multiple frames. Frames use the small molecule's local coordinate space. Ideal for creating multi-model SDFs."
    plugin = nanome.Plugin('Merge As Frames', desc, 'Tools', True)
    plugin.set_plugin_class(MergeAsFrames)
    plugin.run()


if __name__ == '__main__':
    main()
