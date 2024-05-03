const express = require('express');
const mongoose = require('mongoose');
const router = express.Router();

//Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/yourDB', { useNewUrlParser: true, useUnifiedTopology: true });

//Define the student schema
const studentSchema = new mongoose.Schema({
    name: String,
    surname: String,
    stdNumber: String,
    grades: [{
        code: String,
        value: Number
    }],
    averageGrade: Number
});

//Create the student model
const Student = mongoose.model('Student', studentSchema);

//Create a new student
router.post('/student', async (req, res) => {
    try {
        const { name, surname, stdNumber, grades } = req.body;

        // Calculate the average grade for each course
        const courseCodes = [...new Set(grades.map(grade => grade.code))];
        const averageGrades = courseCodes.map(code => {
            const courseGrades = grades.filter(grade => grade.code === code);
            const average = courseGrades.reduce((acc, grade) => acc + grade.value, 0) / courseGrades.length;
            return average;
        });

        // Calculate the average grade for all courses
        const totalAverage = averageGrades.reduce((acc, grade) => acc + grade, 0) / averageGrades.length;

        // Create the new student
        const student = new Student({ name, surname, stdNumber, grades, averageGrade: totalAverage });
        await student.save();

        res.status(201).send(student);
    } catch (error) {
        res.status(400).json({message: error.message});
    }
});

const app = express();
app.use(express.json());
app.use(router);
app.listen(3000, () => console.log('Server is running on port 3000'));