import random

strings = {}



#Only use if location is provided
strings['location'] = [
    'I heard you\'re from {location}, I guess the weather must be beautiful beautiful there. ',
    'I heard you\'re from {location}! Been there myself, its a lovely place. ',
    'I can see you\'re from {location}. It\'s a beautiful place. ',
]

#Only use if skill is provided
strings['skill'] = [
    'I have been looking at your profile. I believe you are skilled enough at {skill}. That must have taken a lot of hours ',
    'Looking at your profile, I could see you have a lot of experience with {skill}. How did you get so good at it?',
    'I can see that you are very skilled in {skill}. When did you start working on it?',
]

strings['awards'] = [
    'Congratulations for your {award}, it is a feat not everyone can achieve... More power to you!',
    'I can also see that you have been awarded {award}! Congratulations to you! How would you describe the joy of the moment you recieved it?',
]

#Only use if certification is provided
strings['certifications'] = [
    'I can see that you are certified in {certificate} by {issuer}. That is quite a feat! Kudos to you...',
    'I can see that you have a highly valuable {issuer} certification in {certificate}. Congratulations to you!',
]

strings['recommendations'] = [
    'I can see that you have been recommended by {giver} for your skills. That is quite a feat! Kudos to you...',
    'I can see in your profile that {giver} had quite a time working with you. I\'m sure ou must be a great person to work with',
    'I can see that you have been recommended by {giver} on your profile. You have really great connections!',
]

#Only use if experience is provided
strings['experience'] = [
    'I can see that you have experience as a {position} at {company}. That is a great thing to have',
    'Being a {position} at {company} must have been quite an experience for you.',
    'I can see that you have worked at {company} for the period of {total_time}. How was the experience?',
]

strings['college'] = [
    'I can see that you are an alumni of {college}. That is something to be proud of... More power to you!',
    'Being an alumni of the presitgious {college} is something that sets you apart from the crowd. Keep crushing it!',
    'It is a delight to know that you were a student of {college}. ',
    'It is a great honor to know that you did your {degree} graduated from {college}. More power to you!',
]

def create_template(data,strings = strings):
    '''
    Creates a template from the strings dictionary
    '''
    random.seed()
    template = ''
    #randomly select from list
    template += random.choice(['Hi', 'Greetings', 'Hello', 'Hey']) + ' '
    template += data['name'].split(' ')[0] + ', '
    key = random.choice( list(strings.keys()) )
    str = random.choice(strings[key])
    try:
        if key == 'location':
            str = str.replace('{location}',data['intro-location'].split(',')[0])
        elif key == 'skill':
            str = str.replace('{skill}',random.choice(data['skills']))
        elif key == 'awards':
            award = random.choice(data['awards'])
            str = str.replace('{award}', award['title']).replace('{issuer}', award['issuer'])
        elif key == 'recommendations':
            recc = random.choice(data['recommendations'])
            str = str.replace('{giver}',recc['giver'])
        elif key == 'certifications':
            cert = random.choice(data['licenses_and_certifications'])
            str = str.replace('{certificate}',cert['name']).replace('{issuer}',cert['issuer'])
        elif key == 'experience':
            exp = random.choice(data['experience'])
            try:
                str = str.replace('{position}',exp['position']['title'])
            except:
                str = str.replace('{position}',exp['position'][0]['title'])
            str = str.replace('{company}',exp['company/institute'])
            str = str.replace('{total_time}',exp['total_duration'])
        elif key == 'college':
            str = str.replace('{college}',data['education'][0]['institute'])
            str = str.replace('{degree}',data['education'][0]['degree'])
        template += str
    except:
        return create_template(data,strings = strings)
    
    return template,key