// Advanced Speech Processing Methods for Accurate FNOL

// Process advanced speech recognition results
function processAdvancedResults(event) {
    let interimTranscript = '';
    let finalTranscript = '';
    let maxConfidence = 0;
    let alternatives = [];
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        
        // Collect all alternatives
        for (let j = 0; j < result.length; j++) {
            alternatives.push({
                transcript: result[j].transcript,
                confidence: result[j].confidence || 0
            });
        }
        
        const transcript = result[0].transcript;
        const confidence = result[0].confidence || 0;
        
        if (result.isFinal) {
            finalTranscript += transcript;
            maxConfidence = Math.max(maxConfidence, confidence);
        } else {
            interimTranscript += transcript;
        }
    }
    
    // Apply advanced processing
    if (finalTranscript) {
        const processedTranscript = this.applyAdvancedProcessing(finalTranscript, alternatives);
        this.currentTranscript = processedTranscript.text;
        this.rawTranscript = finalTranscript;
        
        // Update metrics
        this.updateAdvancedMetrics(processedTranscript.confidence, processedTranscript.clarity, processedTranscript.contextMatch);
        
        // Show error suggestions if needed
        if (processedTranscript.errors.length > 0) {
            this.showErrorSuggestions(processedTranscript.errors);
        }
    }
    
    // Update display
    const displayText = this.currentTranscript || finalTranscript;
    document.getElementById('transcript-text').innerHTML = 
        displayText + '<span style="opacity: 0.5;">' + interimTranscript + '</span>';
}

// Apply advanced processing to transcript
function applyAdvancedProcessing(transcript, alternatives) {
    console.log('🧠 Applying advanced processing to:', transcript);
    
    let processedText = transcript;
    let confidence = 0;
    let clarity = 0;
    let contextMatch = 0;
    let errors = [];
    
    // Calculate average confidence from alternatives
    if (alternatives.length > 0) {
        confidence = alternatives.reduce((sum, alt) => sum + alt.confidence, 0) / alternatives.length;
    }
    
    // Context-aware corrections
    if (this.contextAware) {
        const contextResult = this.applyContextCorrections(processedText, alternatives);
        processedText = contextResult.text;
        contextMatch = contextResult.contextMatch;
        errors = errors.concat(contextResult.errors);
    }
    
    // Grammar and spelling corrections
    const grammarResult = this.applyGrammarCorrections(processedText);
    processedText = grammarResult.text;
    clarity = grammarResult.clarity;
    errors = errors.concat(grammarResult.errors);
    
    // Auto-corrections based on mode
    if (this.errorCorrectionMode === 'auto') {
        processedText = this.applyAutoCorrections(processedText);
    }
    
    return {
        text: processedText,
        confidence: Math.round(confidence * 100),
        clarity: Math.round(clarity * 100),
        contextMatch: Math.round(contextMatch * 100),
        errors: errors
    };
}

// Apply context-aware corrections
function applyContextCorrections(text, alternatives) {
    let correctedText = text;
    let contextMatch = 0;
    let errors = [];
    let corrections = 0;
    
    // Common speech recognition errors in insurance context
    const contextCorrections = {
        'spayed': 'repaired',
        'breaks': 'brakes',
        'steal': 'steel',
        'there car': 'their car',
        'where driving': 'were driving',
        'accident happened': 'accident happened',
        'car accident': 'car accident',
        'rear ended': 'rear-ended',
        'side swiped': 'side-swiped',
        'head on': 'head-on',
        'hit and run': 'hit-and-run',
        'it bother me': 'it bothers me',
        'get it today': 'get it looked at today',
        'so spayed': 'so it can be repaired'
    };
    
    // Apply context corrections
    for (const [wrong, correct] of Object.entries(contextCorrections)) {
        if (correctedText.toLowerCase().includes(wrong.toLowerCase())) {
            const regex = new RegExp(wrong, 'gi');
            correctedText = correctedText.replace(regex, correct);
            corrections++;
            errors.push({
                type: 'context',
                original: wrong,
                corrected: correct,
                position: text.toLowerCase().indexOf(wrong.toLowerCase())
            });
        }
    }
    
    // Check for insurance-related keywords
    let keywordMatches = 0;
    let totalKeywords = 0;
    
    for (const [category, keywords] of Object.entries(this.claimKeywords)) {
        totalKeywords += keywords.length;
        for (const keyword of keywords) {
            if (correctedText.toLowerCase().includes(keyword.toLowerCase())) {
                keywordMatches++;
            }
        }
    }
    
    contextMatch = totalKeywords > 0 ? keywordMatches / totalKeywords : 0;
    
    return {
        text: correctedText,
        contextMatch: contextMatch,
        errors: errors
    };
}

// Apply grammar corrections
function applyGrammarCorrections(text) {
    let correctedText = text;
    let clarity = 0.8; // Base clarity score
    let errors = [];
    
    // Common grammar fixes
    const grammarFixes = {
        ' i ': ' I ',
        'i was': 'I was',
        'i am': 'I am',
        'i have': 'I have',
        'i will': 'I will',
        'i\'ll': 'I\'ll',
        'i\'m': 'I\'m',
        'i\'ve': 'I\'ve',
        ' cant ': ' can\'t ',
        ' wont ': ' won\'t ',
        ' dont ': ' don\'t ',
        ' didnt ': ' didn\'t ',
        ' wasnt ': ' wasn\'t ',
        ' werent ': ' weren\'t ',
        ' isnt ': ' isn\'t ',
        ' arent ': ' aren\'t '
    };
    
    for (const [wrong, correct] of Object.entries(grammarFixes)) {
        if (correctedText.includes(wrong)) {
            correctedText = correctedText.replace(new RegExp(wrong, 'g'), correct);
            clarity += 0.05; // Boost clarity for each fix
        }
    }
    
    // Add punctuation at the end if missing
    if (correctedText && !correctedText.match(/[.!?]$/)) {
        correctedText += '.';
    }
    
    // Capitalize first letter
    if (correctedText) {
        correctedText = correctedText.charAt(0).toUpperCase() + correctedText.slice(1);
    }
    
    return {
        text: correctedText,
        clarity: Math.min(clarity, 1.0),
        errors: errors
    };
}

// Apply auto-corrections
function applyAutoCorrections(text) {
    // Additional auto-corrections for common speech-to-text errors
    const autoCorrections = {
        'at 9 27': 'at 9:27',
        'at 10 30': 'at 10:30',
        'at 11 45': 'at 11:45',
        'june 30 2025': 'June 30, 2025',
        'july 4 2025': 'July 4, 2025',
        'honda accord': 'Honda Accord',
        'toyota camry': 'Toyota Camry',
        'ford f150': 'Ford F-150',
        '2015 to 2018': '2015-2018',
        '2020 to 2023': '2020-2023'
    };
    
    let correctedText = text;
    for (const [pattern, replacement] of Object.entries(autoCorrections)) {
        const regex = new RegExp(pattern, 'gi');
        correctedText = correctedText.replace(regex, replacement);
    }
    
    return correctedText;
}

// Intelligent response generation that considers already provided information
function generateIntelligentResponse(input) {
    const lowerInput = input.toLowerCase();
    
    // Extract information that was already provided
    const providedInfo = this.extractProvidedInformation(input);
    
    if (lowerInput.includes('accident') || lowerInput.includes('crash') || lowerInput.includes('collision')) {
        // Check what information is already provided vs what we need
        let response = "I'm so sorry to hear about your accident. That must have been very frightening and stressful for you.";
        
        const missingInfo = [];
        
        if (!providedInfo.time) {
            missingInfo.push("the time it occurred");
        }
        if (!providedInfo.location) {
            missingInfo.push("the location");
        }
        if (!providedInfo.injuries) {
            missingInfo.push("whether anyone was injured");
        }
        if (!providedInfo.otherDriver) {
            missingInfo.push("information about the other driver");
        }
        
        if (missingInfo.length > 0) {
            response += " I have some of the details, but I need to gather a bit more information. Could you tell me " + missingInfo.join(", ") + "?";
        } else {
            response += " Thank you for providing all those details. Let me make sure I have everything correct and then we can proceed with your claim.";
        }
        
        return {
            message: response,
            extractedData: { 
                incidentType: 'Vehicle Accident', 
                description: input,
                providedInfo: providedInfo
            }
        };
    } else if (lowerInput.includes('theft') || lowerInput.includes('stolen') || lowerInput.includes('burglar')) {
        let response = "I completely understand how violating and upsetting it feels to have your property stolen.";
        
        const missingInfo = [];
        if (!providedInfo.time) missingInfo.push("when you discovered the theft");
        if (!providedInfo.location) missingInfo.push("where it occurred");
        if (!providedInfo.policeReport) missingInfo.push("whether you've filed a police report");
        if (!providedInfo.stolenItems) missingInfo.push("what items were taken");
        
        if (missingInfo.length > 0) {
            response += " I need to gather some additional information. Could you tell me " + missingInfo.join(", ") + "?";
        }
        
        return {
            message: response,
            extractedData: { 
                incidentType: 'Theft/Burglary', 
                description: input,
                providedInfo: providedInfo
            }
        };
    } else if (lowerInput.includes('fire') || lowerInput.includes('smoke') || lowerInput.includes('burn')) {
        let response = "A fire can be absolutely devastating, and I'm so relieved to hear that you're safe.";
        
        const missingInfo = [];
        if (!providedInfo.time) missingInfo.push("when the fire occurred");
        if (!providedInfo.cause) missingInfo.push("what caused the fire");
        if (!providedInfo.fireDepartment) missingInfo.push("whether the fire department responded");
        if (!providedInfo.damageExtent) missingInfo.push("which areas were affected");
        
        if (missingInfo.length > 0) {
            response += " To help process your claim quickly, I need to know " + missingInfo.join(", ") + ".";
        }
        
        return {
            message: response,
            extractedData: { 
                incidentType: 'Fire Damage', 
                description: input,
                providedInfo: providedInfo
            }
        };
    } else if (lowerInput.includes('water') || lowerInput.includes('flood') || lowerInput.includes('leak')) {
        let response = "Water damage can spread quickly and cause extensive problems, so I'm glad you're reporting this promptly.";
        
        const missingInfo = [];
        if (!providedInfo.time) missingInfo.push("when the water damage occurred");
        if (!providedInfo.source) missingInfo.push("the source of the water");
        if (!providedInfo.mitigation) missingInfo.push("what steps you've taken to stop the water");
        if (!providedInfo.damageExtent) missingInfo.push("which areas were affected");
        
        if (missingInfo.length > 0) {
            response += " I need some additional details: " + missingInfo.join(", ") + ".";
        }
        
        return {
            message: response,
            extractedData: { 
                incidentType: 'Water Damage', 
                description: input,
                providedInfo: providedInfo
            }
        };
    } else {
        return {
            message: "Thank you for sharing that information with me. I want to make sure I understand your situation completely. Could you tell me more about what type of incident this was? For example, was this related to a vehicle accident, property theft, fire damage, water damage, or something else?",
            extractedData: { initialDescription: input }
        };
    }
}

// Extract information that was already provided in the input
function extractProvidedInformation(input) {
    const lowerInput = input.toLowerCase();
    const providedInfo = {};
    
    // Time extraction
    const timePatterns = [
        /(\d{1,2}):(\d{2})\s*(am|pm)/i,
        /(\d{1,2})\s*(am|pm)/i,
        /(morning|afternoon|evening|night)/i,
        /(today|yesterday|this morning|last night)/i
    ];
    
    for (const pattern of timePatterns) {
        if (pattern.test(input)) {
            providedInfo.time = true;
            break;
        }
    }
    
    // Date extraction
    const datePatterns = [
        /(january|february|march|april|may|june|july|august|september|october|november|december)/i,
        /\d{1,2}\/\d{1,2}\/\d{4}/,
        /\d{4}/
    ];
    
    for (const pattern of datePatterns) {
        if (pattern.test(input)) {
            providedInfo.date = true;
            break;
        }
    }
    
    // Location indicators
    const locationKeywords = ['street', 'road', 'highway', 'intersection', 'parking', 'driveway', 'at', 'on', 'near'];
    providedInfo.location = locationKeywords.some(keyword => lowerInput.includes(keyword));
    
    // Vehicle information
    const vehicleKeywords = ['honda', 'toyota', 'ford', 'bmw', 'mercedes', 'accord', 'camry', 'civic', 'car', 'truck'];
    providedInfo.vehicleInfo = vehicleKeywords.some(keyword => lowerInput.includes(keyword));
    
    // Injury indicators
    const injuryKeywords = ['hurt', 'injured', 'pain', 'hospital', 'ambulance', 'fine', 'okay', 'uninjured'];
    providedInfo.injuries = injuryKeywords.some(keyword => lowerInput.includes(keyword));
    
    // Other driver information
    providedInfo.otherDriver = lowerInput.includes('other driver') || lowerInput.includes('other car') || lowerInput.includes('they');
    
    // Police report
    providedInfo.policeReport = lowerInput.includes('police') || lowerInput.includes('officer') || lowerInput.includes('report');
    
    // Fire department
    providedInfo.fireDepartment = lowerInput.includes('fire department') || lowerInput.includes('firefighter');
    
    return providedInfo;
}
