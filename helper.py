import matplotlib.pyplot as plt
from IPython import display

plt.ion()


def plot(model_scores, model_mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(model_scores)
    plt.plot(model_mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(model_scores) - 1, model_scores[-1], str(model_scores[-1]))
    plt.text(len(model_mean_scores) - 1, model_mean_scores[-1], str(model_mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)
