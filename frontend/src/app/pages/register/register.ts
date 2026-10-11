import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router,RouterLink } from '@angular/router';
import { DocumentService } from '../../services/document';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrls: ['./register.scss']
})
export class RegisterComponent {

  username = '';
  password = '';
  message = '';
  error = '';

  constructor(
    private documentService: DocumentService,
    private router: Router
  ) {}

  register() {

    this.message = '';
    this.error = '';

    this.documentService
      .register(this.username, this.password)
      .subscribe({
        next: () => {

          this.message = 'Registration successful!';

          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 1000);
        },

        error: (error) => {

          this.error =
            error.error?.detail ||
            error.error?.message ||
            'Registration failed';
        }
      });
  }
}