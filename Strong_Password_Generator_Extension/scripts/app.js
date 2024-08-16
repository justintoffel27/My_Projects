const digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const specials = ['!', '?', '/', '_', '-', '@', '#', '$', '%'];
const lettersLowerCase = [...Array(26)].map((_, i) => String.fromCharCode(i + 97));
const lettersUpperCase = lettersLowerCase.map(letter => letter.toUpperCase());

// Generated random password input
const generatedPasswordInput = document.getElementById('generatedPassword');

// Obtain password length
const passwordLength = document.querySelector('input[type=range]');

// Check checkboxes
const allCheckboxes = document.querySelectorAll('input[type=checkbox]');

const generatePassword = (length) =>
{
    document.getElementById('charLengthSpan').textContent = length;

    // Checking constants/variables
    const includeDigits = document.getElementById('includeDigits').checked;
    const specialChar = document.getElementById('specialChar').checked;
    const letterMix = document.getElementById('letterMix').checked;

    // Reset generated password each time it changes
    generatedPasswordInput.value = '';

    let possiblePasswordChars = [];

    // Checks if to add digits
    if (includeDigits)
    {
        possiblePasswordChars = possiblePasswordChars.concat(digits);
    }

    // Checks if to add special characters
    if (specialChar)
    {
        possiblePasswordChars = possiblePasswordChars.concat(specials);
    }

    if (letterMix)
    {
        possiblePasswordChars = possiblePasswordChars.concat(lettersLowerCase, lettersUpperCase);
    }
    else
    {
        possiblePasswordChars = possiblePasswordChars.concat(lettersLowerCase);
    }

    // Generate password
    for (let i = 0; i < length; i++)
        {
        generatedPasswordInput.value += possiblePasswordChars[Math.floor(Math.random() * possiblePasswordChars.length)];
    }
}

// Initial generation of password
generatePassword(passwordLength.value);

passwordLength.addEventListener('input', () =>
{
    generatePassword(passwordLength.value);
});

allCheckboxes.forEach(check =>
{
    check.addEventListener('change', () =>
    {
        generatePassword(passwordLength.value);
    });
});

// Copy Password
const copyPasswordBtn = document.getElementById('copyPassword');
const confirmation = document.getElementById('confirmation');
copyPasswordBtn.addEventListener('click', () =>
{
    navigator.clipboard.writeText(generatedPasswordInput.value);
    confirmation.classList.add('active');
    setTimeout(() =>
    {
        confirmation.classList.remove('active');
    }, 2000);
});
