import React from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';

const Logout = () => {
    const handleLogout = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.post('/api/logout', {}, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            localStorage.removeItem('token');
            Swal.fire('Success', 'Logout successful', 'success');
        } catch (error) {
            Swal.fire('Error', 'Logout failed', 'error');
        }
    };

    return (
        <button onClick={handleLogout}>Logout</button>
    );
};

export default Logout;