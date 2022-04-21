import nanome
from nanome.util import async_callback, enums, Logs


class MergeAsFrames(nanome.AsyncPluginInstance):
    def start(self):
        self.set_plugin_list_button(enums.PluginListButtonType.run, 'Merge')
        self.delete_originals = True
        self.on_advanced_settings()

    def on_advanced_settings(self):
        self.delete_originals = not self.delete_originals
        text = 'Delete Entries ■' if self.delete_originals else 'Delete Entries □'
        self.set_plugin_list_button(enums.PluginListButtonType.advanced_settings, text)

    @async_callback
    async def on_run(self):
        shallow = await self.request_complex_list()
        indices_selected = [c.index for c in shallow if c.get_selected()]

        if len(indices_selected) < 2:
            self.send_notification(enums.NotificationTypes.warning, 'Please select multiple entries.')
            return

        complexes = await self.request_complexes(indices_selected)

        new_complex = nanome.structure.Complex()
        new_complex.name = complexes[0].name + ' Merged'

        for complex in complexes:
            complex = complex.convert_to_frames()
            complex.set_all_selected(False)
            for molecule in complex.molecules:
                new_complex.add_molecule(molecule)

        self.add_to_workspace([new_complex])

        if self.delete_originals:
            self.remove_from_workspace(complexes)


def main():
    plugin = nanome.Plugin('Merge As Frames', 'A Nanome plugin to merge multiple entries into the frames of a new entry. Select entries and then press the Merge button.', 'Tools', True)
    plugin.set_plugin_class(MergeAsFrames)
    plugin.run()


if __name__ == '__main__':
    main()
