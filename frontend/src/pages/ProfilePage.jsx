import React from 'react';
import AlertBadge from '../components/AlertBadge';

const ProfilePage = () => {
    return (
        <div>
            <h2>Dietary Profile</h2>
            <p>Your current restrictions:</p>
            <div>
                <AlertBadge message="Peanut Allergy" type="danger" />
                <AlertBadge message="Vegan" type="warning" />
            </div>
        </div>
    );
};

export default ProfilePage;
