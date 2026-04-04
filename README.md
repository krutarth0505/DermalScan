🧴 DermalScan: AI Facial Skin Aging Detection App

DermalScan is a deep learning–based web application that detects and classifies facial skin aging conditions such as Wrinkles, Dark Spots, Puffy Eyes, and Clear Skin using a pretrained EfficientNetB0 model.
The system integrates face detection, image preprocessing, classification, confidence visualization, and a user-friendly web interface.

📌 Project Overview:

The goal of DermalScan is to automate facial skin aging analysis using Artificial Intelligence.
Users can upload or capture a facial image, and the system will:

Detect the face

Identify the skin condition

Display confidence scores

Show annotated output images

Allow result downloads

🧠 Problem Statement:

The objective is to develop a deep learning–based system that can detect and classify facial aging signs—such as wrinkles, dark spots, puffy eyes, and clear skin—using a pretrained EfficientNetB0 model.

The pipeline includes:

Face detection using Haar Cascades

Image preprocessing and data augmentation

Skin condition classification with percentage confidence

A web-based frontend to visualize results with annotated bounding boxes and labels

📂 Dataset Description:

Source: Kaggle

Classes:

Wrinkles

Dark Spots

Puffy Eyes

Clear Skin

📊 Dataset Preparation:

Initial dataset contained ~300 images per class

Clear Skin images were manually cleaned and verified

Data augmentation techniques were applied

Final balanced dataset contained 409 images per class

<img width="1536" height="1024" alt="Dataset Overview" src="https://github.com/user-attachments/assets/0a3f0ae3-517b-4abc-821d-7a8940b2a016" />
🔗 Dataset Link

👉 📥 Download Dataset from Google Drive
https://drive.google.com/drive/folders/1oDO54S6tc-GX5w61X9AvWG-z8dgvZoKy?usp=sharing

🧩 Project Modules (End-to-End Workflow)
🔹 Module 1: Data Collection & Cleaning

Collected facial skin images from Kaggle

Removed noisy and mislabeled images

Manual verification for Clear Skin class

🔹 Module 2: Data Preprocessing

Image resizing to 224 × 224

RGB color conversion

Normalization using EfficientNet preprocessing

Data augmentation:

Rotation

Horizontal flipping

Zooming

🔹 Module 3: Face Detection

Implemented Haar Cascade Classifier

Face region extracted before classification

Fallback to full-image analysis if no face is detected

🔹 Module 4: Feature Extraction

Used EfficientNetB0 pretrained on ImageNet

Automatic extraction of:

Texture features

Spatial facial patterns

Global Average Pooling (GAP) used to reduce dimensionality

🔹 Module 5: Model Architecture

EfficientNetB0 backbone

Transfer learning applied

Fully connected layers for classification

Output layer with Softmax activation

🔹 Module 6: Model Training

Optimizer: Adam

Loss Function: Categorical Cross-Entropy

Dataset split:

Training: 80%

Validation: 20%

Techniques used:

Early Stopping

Model Checkpointing

🔹 Module 7: Model Evaluation

Achieved ~94% validation accuracy

Stable training with minimal overfitting

Reliable confidence predictions

<img width="767" height="613" alt="Model Accuracy" src="https://github.com/user-attachments/assets/e99302bd-b1d0-4cbb-842a-6e8774c57d39" />
🔹 Module 8: Web Application (UI)

Built using Streamlit.

Features:

Image upload & live camera input

Annotated output image

Confidence score display

Probability distribution

Processing time display

Download results (CSV & annotated image)

<img width="1914" height="794" alt="Screenshot 2026-01-14 211732" src="https://github.com/user-attachments/assets/c96d101a-5c5f-4889-87e8-69f9cdc111f1" />
<img width="1891" height="828" alt="Screenshot 2026-01-14 211906" src="https://github.com/user-attachments/assets/9e3cda78-060a-471a-a957-e181143b8d3e" />
<img width="1900" height="836" alt="Screenshot 2026-01-14 211947" src="https://github.com/user-attachments/assets/d1953dc1-4441-42ef-8273-dcd2298ab09f" />



🖥️ Technologies Used

Programming Language: Python

Deep Learning: TensorFlow, Keras

Model: EfficientNetB0

Computer Vision: OpenCV

Web Framework: Streamlit

Data Handling: NumPy, Pandas

📈 Results

Validation Accuracy: ~94%

Clear and confident predictions

Real-time inference capability

User-friendly interface

⚠️ Challenges

Noisy dataset

Class imbalance

Lighting variations in facial images

Limitations of Haar Cascade for complex angles

🚧 Limitations

Limited dataset size

Performance depends on image quality

Haar Cascade struggles with side faces and poor lighting

🔮 Future Scope

Add more skin conditions (Acne, Pigmentation, Fine Lines)

Multi-label skin condition detection

Replace Haar Cascade with MTCNN / YOLO

Personalized skincare recommendations

Mobile application integration

🔗 Project Links

GitHub Repository:
👉 https://github.com/janhavijawalkar/AI_DermaScan

Dataset Link:
👉 https://drive.google.com/drive/folders/1oDO54S6tc-GX5w61X9AvWG-z8dgvZoKy?usp=sharing

👩‍🎓 Author

Janhavi Jawalkar
B.Tech – Computer Science Engineering
