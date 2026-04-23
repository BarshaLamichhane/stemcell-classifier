import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UtilityNav } from './utility-nav';

describe('UtilityNav', () => {
  let component: UtilityNav;
  let fixture: ComponentFixture<UtilityNav>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UtilityNav]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UtilityNav);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
