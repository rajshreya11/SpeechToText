import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Transcribe } from './transcribe';

describe('Transcribe', () => {
  let component: Transcribe;
  let fixture: ComponentFixture<Transcribe>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Transcribe],
    }).compileComponents();

    fixture = TestBed.createComponent(Transcribe);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
