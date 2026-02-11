// Tab switching
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        
        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update active content
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${targetTab}-content`) {
                content.classList.add('active');
            }
        });
    });
});

// File input handlers
const resumeFile = document.getElementById('resume-file');
const resumeDisplay = document.getElementById('resume-display');
const qaResumeFile = document.getElementById('qa-resume-file');
const qaResumeDisplay = document.getElementById('qa-resume-display');

resumeFile.addEventListener('change', (e) => {
    updateFileDisplay(e.target, resumeDisplay);
});

qaResumeFile.addEventListener('change', (e) => {
    updateFileDisplay(e.target, qaResumeDisplay);
});

function updateFileDisplay(input, display) {
    if (input.files.length > 0) {
        const fileName = input.files[0].name;
        display.innerHTML = `
            <span class="file-name">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/>
                    <polyline points="13 2 13 9 20 9"/>
                </svg>
                ${fileName}
            </span>
        `;
    }
}

// Resume Matching Form
const matchForm = document.getElementById('match-form');
const matchBtn = document.getElementById('match-btn');
const matchProgress = document.getElementById('match-progress');
const matchResult = document.getElementById('match-result');

matchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('resume_file', resumeFile.files[0]);
    formData.append('job_description', document.getElementById('job-description').value);
    
    // Show progress, hide result
    matchProgress.style.display = 'block';
    matchResult.style.display = 'none';
    matchBtn.disabled = true;
    
    // Simulate progress steps
    await simulateProgress('match');
    
    try {
        const response = await fetch('/match', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze resume');
        }
        
        const data = await response.json();
        displayMatchResult(data.match_score);
        
    } catch (error) {
        alert('Error: ' + error.message);
        matchProgress.style.display = 'none';
    } finally {
        matchBtn.disabled = false;
    }
});

async function simulateProgress(type) {
    const prefix = type === 'match' ? '' : 'qa-';
    const steps = [
        `${prefix}step-upload`,
        `${prefix}step-extract`,
        `${prefix}step-analyze`,
        `${prefix}step-complete`
    ];
    const progressFill = document.getElementById(`${type}-progress-fill`);
    
    for (let i = 0; i < steps.length; i++) {
        // Mark current step as active
        const currentStep = document.getElementById(steps[i]);
        currentStep.classList.add('active');
        
        // Update progress bar
        const progress = ((i + 1) / steps.length) * 100;
        progressFill.style.width = `${progress}%`;
        
        // Mark previous steps as completed
        if (i > 0) {
            const prevStep = document.getElementById(steps[i - 1]);
            prevStep.classList.remove('active');
            prevStep.classList.add('completed');
        }
        
        // Wait before next step
        await new Promise(resolve => setTimeout(resolve, 800));
    }
}

function displayMatchResult(score) {
    matchProgress.style.display = 'none';
    matchResult.style.display = 'block';
    
    // Animate score
    const scoreValue = document.getElementById('score-value');
    const scoreProgress = document.getElementById('score-progress');
    const interpretation = document.getElementById('result-interpretation');
    
    // Calculate circle progress
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (score / 100) * circumference;
    
    // Animate number
    let currentScore = 0;
    const duration = 1500;
    const increment = score / (duration / 16);
    
    const timer = setInterval(() => {
        currentScore += increment;
        if (currentScore >= score) {
            currentScore = score;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(currentScore);
    }, 16);
    
    // Animate circle
    setTimeout(() => {
        scoreProgress.style.strokeDashoffset = offset;
    }, 100);
    
    // Show interpretation
    let message, className;
    if (score >= 80) {
        message = '🎉 Excellent Match! This candidate is highly suitable for the position.';
        className = 'excellent';
    } else if (score >= 60) {
        message = '✅ Good Match! This candidate has strong potential for the role.';
        className = 'good';
    } else if (score >= 40) {
        message = '⚠️ Fair Match. The candidate has some relevant skills but may need development.';
        className = 'fair';
    } else {
        message = '❌ Low Match. This candidate may not be the best fit for this position.';
        className = 'poor';
    }
    
    interpretation.textContent = message;
    interpretation.className = `result-interpretation ${className}`;
    
    // Scroll to result
    setTimeout(() => {
        matchResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 500);
}

// Q&A Form
const qaForm = document.getElementById('qa-form');
const qaBtn = document.getElementById('qa-btn');
const qaProgress = document.getElementById('qa-progress');
const qaResult = document.getElementById('qa-result');

qaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('resume_file', qaResumeFile.files[0]);
    formData.append('question', document.getElementById('question').value);
    
    // Show progress, hide result
    qaProgress.style.display = 'block';
    qaResult.style.display = 'none';
    qaBtn.disabled = true;
    
    // Simulate progress steps
    await simulateProgress('qa');
    
    try {
        const response = await fetch('/qa', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to get answer');
        }
        
        const data = await response.json();
        displayQAResult(data.answer);
        
    } catch (error) {
        alert('Error: ' + error.message);
        qaProgress.style.display = 'none';
    } finally {
        qaBtn.disabled = false;
    }
});

function displayQAResult(answer) {
    qaProgress.style.display = 'none';
    qaResult.style.display = 'block';
    
    const answerText = document.getElementById('answer-text');
    answerText.textContent = answer;
    
    // Scroll to result
    setTimeout(() => {
        qaResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
}

// Reset progress on tab switch
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Reset match progress
        matchProgress.style.display = 'none';
        matchResult.style.display = 'none';
        document.querySelectorAll('#match-progress .step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
        document.getElementById('match-progress-fill').style.width = '0%';
        
        // Reset QA progress
        qaProgress.style.display = 'none';
        qaResult.style.display = 'none';
        document.querySelectorAll('#qa-progress .step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
        document.getElementById('qa-progress-fill').style.width = '0%';
    });
});
