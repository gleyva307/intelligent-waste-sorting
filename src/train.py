import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight

# ==================== PARÁMETROS ====================
DATASET_PATH = "C:/Users/USUARIO/OneDrive/Escritorio/dataset"
IMG_HEIGHT, IMG_WIDTH = 180, 180
BATCH_SIZE = 32
EPOCHS = 50
SEED = 123

# ==================== CARGA DE DATOS ====================
# Train / Validation (80/20)
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE)

# Obtener nombres de clases
class_names = train_ds.class_names
num_classes = len(class_names)
print(f"✅ Clases detectadas: {class_names}")

with open("class_names.json", "w") as f:
    json.dump(class_names, f)

# ==================== AUMENTO DE DATOS ====================
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.25),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.15),
    layers.RandomBrightness(0.2),
    layers.RandomTranslation(0.1, 0.1),
])

# ==================== PREPROCESAMIENTO ====================
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

train_ds = train_ds.map(lambda x, y: (data_augmentation(preprocess_input(x), training=True), y))
val_ds = val_ds.map(lambda x, y: (preprocess_input(x), y))

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# ==================== BALANCE DE CLASES ====================
y_train_labels = np.concatenate([y.numpy() for x, y in train_ds])
class_weights = compute_class_weight(class_weight="balanced", classes=np.unique(y_train_labels), y=y_train_labels)
class_weight_dict = dict(enumerate(class_weights))
print("✅ Pesos de clase calculados:", class_weight_dict)

# ==================== MODELO ====================
base_model = tf.keras.applications.MobileNetV2(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
                                               include_top=False,
                                               weights="imagenet")
base_model.trainable = False  # Fine-tuning luego

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0003),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# ==================== CALLBACKS ====================
early_stop = callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor='val_loss')
checkpoint = callbacks.ModelCheckpoint("best_model.keras", save_best_only=True, monitor='val_accuracy', mode='max')
reduce_lr = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=5, min_lr=1e-6)

# ==================== ENTRENAMIENTO ====================
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[early_stop, checkpoint, reduce_lr],
    class_weight=class_weight_dict
)

# ==================== FINE-TUNING ====================
base_model.trainable = True
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

fine_tune_epochs = 20
total_epochs = EPOCHS + fine_tune_epochs

history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=total_epochs,
    initial_epoch=history.epoch[-1],
    callbacks=[early_stop, checkpoint, reduce_lr],
    class_weight=class_weight_dict
)

# ==================== GUARDADO ====================
model.save("waste_classifier_model.keras")
print("✅ Modelo final guardado como 'waste_classifier_model.keras'")

# ==================== VISUALIZACIÓN ====================
def plot_history(histories, title='Model Training History'):
    acc = []
    val_acc = []
    loss = []
    val_loss = []
    for h in histories:
        acc += h.history['accuracy']
        val_acc += h.history['val_accuracy']
        loss += h.history['loss']
        val_loss += h.history['val_loss']

    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Entrenamiento')
    plt.plot(val_acc, label='Validación')
    plt.title('Precisión')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Entrenamiento')
    plt.plot(val_loss, label='Validación')
    plt.title('Pérdida')
    plt.legend()

    plt.suptitle(title)
    plt.savefig("training_history.png")
    plt.show()

plot_history([history, history_fine])
