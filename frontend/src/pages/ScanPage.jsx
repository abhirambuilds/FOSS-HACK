import React from 'react';
import CameraView from '../components/CameraView';
import ResultCard from '../components/ResultCard';

const ScanPage = () => {
    return (
        <div>
            <h2>Scan Food Label</h2>
            <CameraView />
            <div style={{ marginTop: '20px' }}>
                <h3>Mock Results:</h3>
                <ResultCard title="Sample Snack" score="-0.42" verdict="Unhealthy" />
            </div>
        </div>
    );
};

export default ScanPage;
