import gym
import random
import numpy as np
import keras

from statistics import mean, median
from collections import Counter
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

TRAINING_DATA_FILENAME = 'training_data_cart_pole.npy'
learningRate = 1e-3

env = gym.make('CartPole-v0')
env.reset()
goal_steps = 200
score_requirement = 50
initial_games = 10000


def play_random_games():
    for episode in range(5):
        env.reset()
        for t in range(goal_steps):
            env.render()
            action = env.action_space.sample()
            observation, reward, done, info = env.step(action)
            if done:
                break

#play_random_games();

def initial_population():
    training_data = []
    scores = []
    accepted_scores = []

    for _ in range(initial_games):
        score = 0
        game_memory = []
        previous_observation = []
        
        for _ in range(goal_steps):
            action = random.randrange(0, 2) # take one of random actions available in this env
            observation, reward, done, info = env.step(action)

            if len(previous_observation) > 0:
                game_memory.append([previous_observation, action])

            previous_observation = observation
            score += reward
            if done:
                break

        if score >= score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                # converto to one-hot encoding
                if data[1] == 1:
                    output = [0, 1]
                else:
                    output = [1,0]
                # append observation and action taken
                training_data.append([data[0], output])

        env.reset()
        scores.append(score)

    training_data_save = np.array(training_data)
    np.save(TRAINING_DATA_FILENAME, training_data_save)

    print('Average accepted score:', mean(accepted_scores))
    print('Median:', median(accepted_scores))
    print(Counter(accepted_scores))

    return training_data

def neural_network_model(input_size):
    model = Sequential()
    #network = input_data(shape = [None, input_size, 1], name='input')
    model.add(Dense(units=128, input_shape=(input_size, )))
    model.add(Activation('relu'))
    model.add(Dropout(0.8))

    model.add(Dense(units=256))
    model.add(Activation('relu'))
    model.add(Dropout(0.8))

    model.add(Dense(units=512))
    model.add(Activation('relu'))
    model.add(Dropout(0.8))

    model.add(Dense(units=256))
    model.add(Activation('relu'))
    model.add(Dropout(0.8))

    model.add(Dense(units=128))
    model.add(Activation('relu'))
    model.add(Dropout(0.8))

    model.add(Dense(units=2))
    model.add(Activation('softmax'))

    model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

    return model


#initial_population()
training_data = np.load(TRAINING_DATA_FILENAME)
print(training_data.shape)
print(training_data[0][0].shape)
print(training_data[0][1])

X = np.array([i[0] for i in training_data]).reshape(len(training_data), 4)
y = np.array([i[1] for i in training_data]).reshape(len(training_data), 2)
#print(X[0:2, :])
#print(y.shape)
#X = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]), 1)
#y = np.array([i[1] for i in training_data]).reshape(len(training_data), 2, 1)
#print(y.shape)
model = neural_network_model(len(X[0]))
model.fit(X, y, epochs=5, batch_size=128)
