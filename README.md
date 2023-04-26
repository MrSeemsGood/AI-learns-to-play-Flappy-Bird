# Flappy Bird AI
![изображение](https://user-images.githubusercontent.com/87701031/234704986-39aedb99-7480-459d-920b-31bd5bc50aec.png)


AI learns to play Flappy Bird. And then actually plays it!

**Neural Network structure:**

```
y coordinate                                      \
vertical velocity                                 |   -> (7 hidden neurons)   ->  \  output 1  -> if output1 > output2, the bird jumps.
distance (along the x axis) to the next column    |                               /  output 2
gap coordinates in the next column                /
```

**Learning:**

50 birds per generation; best-performing bird passes its weights to the next generation with noise applied. Amplitude of the noise can be defined by the `noise_order` argument of `FlappyBirdAi` class. By default it is 0.04, which means weights are multiplied by a random float in range [0.96, 1.04].

*P.S. Images used in this game AREN'T MINE, I took them from the Internet.*

*P.S.S. thanks to https://flappybird-ai.netlify.app/ for providing a general idea on how to implement the learning algorithm!*

---

Искуственный интеллект учится играть в Flappy Bird. А потом играет!

**Структура нейронной сети:**

```
координата по у                                   \
вертикальная скорость                             |   -> (7 скрытых нейронов)   ->  \  выход 1  -> если выход 1 больше, птичка прыгает.
расстояние (по оси х) до следующей колонны        |                                 /  выход 2
координаты прорези в следующей колонне            /
```

**Обучение:**

50 птичек на каждое поколение; веса птички с лучшим результатом используются следующим поколением, с наложенным шумом. Амплитуда шума может быть настроена с помощью параметра `noise_order` класса `FlappyBirdAi`. По умолчанию - 0.04, т.е. веса умножаются на случайную десятичную дробь в диапазоне [0.96, 1.04].

*P.S. Картинки, используемые в игре, НЕ МОИ. Я взял их из Интернета.*

*P.S.S. спасибо https://flappybird-ai.netlify.app/ за предоставление идеи и базового понимания, как обучать алгоритм!*


