from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import flower_rec as fr
# import pickle

Builder.load_string('''
<FlowerImage>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (720, 480)
        play: True
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')

# with open(os.path.abspath('./mod.pkl'), 'rb') as f:
#     model = pickle.load(f)


class FlowerImage(BoxLayout):

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their type of flower.
        """

        camera = self.ids['camera']
        camera.export_to_png("Test/IMG.png")
        print('Captured')
        self.ids['camera'].play = False

    def main(self):
        test_root = os.path.abspath('./'+'Test/')
        image_url = 'file://'+test_root+'/IMG.png'

        pred = fr.img_pred(image_url)

        self.add_widget(Label(text=pred, text_size=(600, None), line_height=1.5))





class ImageRecognition(App):

    @property
    def build(self):
        return FlowerImage


if __name__ == "__main__":
    app = ImageRecognition()
    app.run()
